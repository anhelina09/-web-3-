from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from courses.models import Student, Branch, StudentGroup, Subject 
from .models import CustomUser 

def login_view(request):
    if request.method == 'POST':
        login_data = request.POST.get('phone', '').strip() # Дані з поля вводу (телефон або email)
        password = request.POST.get('password')

        if not login_data or not password:
            return render(request, 'registration/login.html', {'error': 'Будь ласка, введіть номер телефону/email та пароль.'})

        # Шукаємо користувача за телефоном або імейлом
        user_obj = CustomUser.objects.filter(Q(email=login_data) | Q(phone=login_data)).first()
        
        if user_obj is not None:
            # Оскільки USERNAME_FIELD тепер 'phone', передаємо телефон у параметр username
            user = authenticate(request, username=user_obj.phone, password=password)
            if user is not None:
                if not user.is_active: # Бізнес-правило: неактивний користувач не може увійти
                    return render(request, 'registration/login.html', {'error': 'Ваш акаунт деактивовано.'})
                login(request, user)
                return redirect('dashboard')

        # ТЗ (Едж-кейс 4.1): Однаковий текст помилки як для невірного пароля, так і для неіснуючого юзера
        return render(request, 'registration/login.html', {'error': 'Неправильний номер телефону або пароль.'})

    return render(request, 'registration/login.html')

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # ФІКС: Перевіряємо роль великими літерами, як у моделі (ADMIN / TEACHER)
    if request.user.role == 'TEACHER':
        return render(request, 'dashboard/teacher.html')
    else:
        return render(request, 'dashboard/admin.html')
    
def student_list_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    students = Student.objects.all() 
    return render(request, 'core/student_list.html', {'students': students})

def branch_list_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    branches = Branch.objects.all() 
    return render(request, 'core/branch_list.html', {'branches': branches})

def group_list_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    groups = StudentGroup.objects.all()
    return render(request, 'core/group_list.html', {'groups': groups})

def subject_list_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    subjects = Subject.objects.all()
    return render(request, 'core/subject_list.html', {'subjects': subjects})

def logout_view(request):
    logout(request)
    return redirect('login')