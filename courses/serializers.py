from rest_framework import serializers
from django.db.models import Q
from .models import (
    Branch, Subject, SubscriptionPlan, Student, 
    StudentGroup, Lesson, Attendance, StudentSubscription
)

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

    def validate(self, data):
        # ТЗ 4.3: Унікальність назви предмета в межах однієї філії
        name = data.get('name')
        branch = data.get('branch')
        
        # Перевірка для створення та оновлення
        queryset = Subject.objects.filter(name__iexact=name, branch=branch)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
            
        if queryset.exists():
            raise serializers.ValidationError(
                {"name": f"Предмет з назвою '{name}' вже існує у цій філії."}
            )
        return data


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'


class StudentGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentGroup
        fields = '__all__'

    def validate(self, data):
        # ТЗ 4.5: Не можна додати студента з іншої філії до групи
        branch = data.get('branch')
        students = data.get('students', [])

        if branch and students:
            for student in students:
                if student.branch != branch:
                    raise serializers.ValidationError(
                        {"students": f"Студент {student.first_name} {student.last_name} належить до іншої філії ({student.branch.name})."}
                    )
        return data


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'


class StudentSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSubscription
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

    def validate(self, data):
        date = data.get('date')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        teacher = data.get('teacher')
        lesson_type = data.get('lesson_type')
        group = data.get('group')
        student = data.get('student')

        if start_time >= end_time:
            raise serializers.ValidationError("Час початку уроку не може бути більшим або рівним часу завершення.")

        # Базовий фільтр для пошуку накладок за формулою з ТЗ: start_1 < end_2 AND start_2 < end_1
        # Скасовані уроки (CANCELLED) за ТЗ повністю ігноруються при перевірці конфліктів
        overlapping_lessons = Lesson.objects.filter(
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exclude(status='CANCELLED')

        # Якщо ми оновлюємо існуючий урок, виключаємо його з перевірки самого себе
        if self.instance:
            overlapping_lessons = overlapping_lessons.exclude(pk=self.instance.pk)

        # 1. ТЗ 4.7.3: Перевірка конфлікту вчителя
        teacher_conflict = overlapping_lessons.filter(teacher=teacher)
        if teacher_conflict.exists():
            raise serializers.ValidationError(
                f"Конфлікт вчителя! Цей викладач вже веде інший урок у період {start_time}-{end_time} на дату {date}."
            )

        # Збираємо список ID студентів, яких треба перевірити на конфлікт часу
        students_to_check = []
        if lesson_type == 'INDIVIDUAL' and student:
            students_to_check.append(student.id)
        elif lesson_type == 'GROUP' and group:
            # ТЗ: Для групових занять перевіряємо ВСІХ поточних членів групи
            students_to_check = list(group.students.values_list('id', flat=True))

        # 2. ТЗ 4.7.3: Перевірка конфлікту студентів
        if students_to_check:
            # Шукаємо уроки, де перетинається час і де беруть участь наші студенти
            student_conflict = overlapping_lessons.filter(
                Q(student_id__in=students_to_check) | Q(group__students__id__in=students_to_check)
            ).distinct()

            if student_conflict.exists():
                raise serializers.ValidationError(
                    f"Конфлікт розкладу студентів! Один або декілька студентів уже записані на інше заняття у цей час ({start_time}-{end_time})."
                )

        return data


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

    def validate(self, data):
        lesson = data.get('lesson')
        student = data.get('student')

        # ТЗ 4.8: Не можна ставити відвідуваність на скасований урок
        if lesson and lesson.status == 'CANCELLED':
            raise serializers.ValidationError("Неможливо відмітити відвідуваність для скасованого уроку.")

        # ТЗ 4.8: Студент має бути учасником цього уроку (в індивідуальному або бути в групі)
        if lesson and student:
            if lesson.lesson_type == 'INDIVIDUAL' and lesson.student != student:
                raise serializers.ValidationError("Цей студент не записаний на дане індивідуальне заняття.")
            elif lesson.lesson_type == 'GROUP' and lesson.group and not lesson.group.students.filter(id=student.id).exists():
                raise serializers.ValidationError("Цей студент не є учасником групи, для якої проводиться урок.")

        return data