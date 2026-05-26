from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import (
    Branch, Subject, Student, StudentGroup, 
    SubscriptionPlan, StudentSubscription, Lesson, Attendance
)
from .serializers import (
    BranchSerializer, SubjectSerializer, StudentSerializer, StudentGroupSerializer,
    SubscriptionPlanSerializer, StudentSubscriptionSerializer, LessonSerializer, AttendanceSerializer
)



class IsAdminUserRole(permissions.BasePermission):
    """Доступ дозволено тільки користувачам з роллю ADMIN"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'


class ScheduleAndAttendancePermission(permissions.BasePermission):
    """
    Права доступу для уроків та відвідуваності:
    - ADMIN: Повний доступ.
    - TEACHER: Тільки перегляд та відмітка відвідуваності на власних уроках.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Адмін може робити все
        if request.user.role == 'ADMIN':
            return True
        # Вчитель може тільки дивитися або редагувати (без створення/видалення через загальний URL)
        if request.user.role == 'TEACHER':
            return request.method in permissions.SAFE_METHODS or request.method in ['PUT', 'PATCH']
        return False


# ==========================================
# 🎮 КОНТРОЛЕРИ (VIEWSETS З ОПТИМІЗАЦІЄЮ ЗАПИТІВ N+1)
# ==========================================

class BranchViewSet(viewsets.ModelViewSet):
    """Керування філіями (Тільки ADMIN)"""
    serializer_class = BranchSerializer
    permission_classes = [IsAdminUserRole]

    def get_queryset(self):
        # Повертає тільки активні філії для лістингів за ТЗ, сортує за ID
        return Branch.objects.filter(status='ACTIVE').order_by('-id')


class SubjectViewSet(viewsets.ModelViewSet):
    """Керування предметами (Тільки ADMIN)"""
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminUserRole]

    def get_queryset(self):
        # ФІКС ФАЗИ 3: select_related('branch') оптимізує запит до філії предмета
        return Subject.objects.filter(status='ACTIVE').select_related('branch').order_by('-id')


class StudentViewSet(viewsets.ModelViewSet):
    """Керування студентами (Тільки ADMIN)"""
    serializer_class = StudentSerializer
    permission_classes = [IsAdminUserRole]

    def get_queryset(self):
        # ФІКС ФАЗИ 3: select_related('branch') прибирає N+1 запит при читанні студентів
        return Student.objects.filter(status='ACTIVE').select_related('branch').order_by('-id')


class StudentGroupViewSet(viewsets.ModelViewSet):
    """Керування групами студентів (Тільки ADMIN)"""
    serializer_class = StudentGroupSerializer
    permission_classes = [IsAdminUserRole]

    def get_queryset(self):
        # ФІКС ФАЗИ 3: Одночасне завантаження зв'язків та M2M списку студентів через prefetch_related
        return StudentGroup.objects.filter(status='ACTIVE').select_related(
            'branch', 'subject', 'teacher'
        ).prefetch_related('students').order_by('-id')


class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    """Керування тарифною сіткою підписок (Тільки ADMIN)"""
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAdminUserRole]

    def get_queryset(self):
        return SubscriptionPlan.objects.filter(status='ACTIVE').select_related('branch').prefetch_related('subjects').order_by('-id')


class StudentSubscriptionViewSet(viewsets.ModelViewSet):
    """Прив'язка підписок до студентів (Тільки ADMIN)"""
    serializer_class = StudentSubscriptionSerializer
    permission_classes = [IsAdminUserRole]

    def get_queryset(self):
        return StudentSubscription.objects.select_related('student', 'subject', 'plan').order_by('-id')


class LessonViewSet(viewsets.ModelViewSet):
    """Керування розкладом уроків (ADMIN — повністю, TEACHER — тільки свої)"""
    serializer_class = LessonSerializer
    permission_classes = [ScheduleAndAttendancePermission]

    def get_queryset(self):
        # ФІКС ФАЗИ 3: Оптимізація зв'язків уроку
        queryset = Lesson.objects.select_related('subject', 'teacher', 'group', 'student')
        
        # ТЗ 3: Вчитель може бачити тільки свій власний розклад уроків
        if self.request.user.role == 'TEACHER':
            return queryset.filter(teacher=self.request.user).order_by('date', 'start_time')
        
        return queryset.order_by('-date', '-start_time')


class AttendanceViewSet(viewsets.ModelViewSet):
    """Журнал відвідуваності уроків (ADMIN — повністю, TEACHER — тільки для своїх уроків)"""
    serializer_class = AttendanceSerializer
    permission_classes = [ScheduleAndAttendancePermission]

    def get_queryset(self):
        # ФІКС ФАЗИ 3: Оптимізація запитів для відвідуваності
        queryset = Attendance.objects.select_related('student', 'lesson', 'lesson__subject')
        
        # ТЗ 3: Вчитель може переглядати/ставити відвідуваність ТІЛЬКИ для своїх уроків
        if self.request.user.role == 'TEACHER':
            return queryset.filter(lesson__teacher=self.request.user).order_by('-id')
            
        return queryset.order_by('-id')

    def perform_create(self, serializer):
        # Додаткова бізнес-перевірка при створенні: вчитель не може виставити присутність на чужий урок
        if self.request.user.role == 'TEACHER':
            lesson = serializer.validated_data.get('lesson')
            if lesson.teacher != self.request.user:
                raise PermissionDenied("Ви не можете відмічати відвідуваність на чужому уроці.")
        serializer.save()