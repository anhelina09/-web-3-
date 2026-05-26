from django.urls import path
from . import views  # Імпортуємо views цього ж додатка

urlpatterns = [
    # Авторизація та аутентифікація
    path('', views.login_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Єдиний розумний дашборд (автоматично розділяє вчителів та адмінів)
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Списки сутностей для відображення в інтерфейсі
    path('branches/', views.branch_list_view, name='branch_list'),
    path('groups/', views.group_list_view, name='group_list'),
    path('students/', views.student_list_view, name='student_list'),
    path('subjects/', views.subject_list_view, name='subject_list'),
]