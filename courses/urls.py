from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BranchViewSet, SubjectViewSet, StudentViewSet, StudentGroupViewSet,
    SubscriptionPlanViewSet, StudentSubscriptionViewSet, LessonViewSet, AttendanceViewSet
)

# Створюємо DRF Роутер для автоматичної генерації REST API маршрутів
router = DefaultRouter()
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'groups', StudentGroupViewSet, basename='group')
router.register(r'subscription-plans', SubscriptionPlanViewSet, basename='subscription-plan')
router.register(r'student-subscriptions', StudentSubscriptionViewSet, basename='student-subscription')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'attendance', AttendanceViewSet, basename='attendance')

urlpatterns = [
    # Підключаємо всі згенеровані маршрути роутера
    path('', include(router.urls)),
]