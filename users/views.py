from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from courses.models import Student, Branch, StudentGroup, Subject
from .models import CustomUser


def login_view(request):
    if request.method == 'POST':
        login_data = request.POST.get('phone', '').strip()
        password = request.POST.get('password')

        user_obj = CustomUser.objects.filter(
            Q(email=login_data) | Q(phone=login_data)
        ).first()

        if user_obj:
            user = authenticate(
                request,
                username=user_obj.phone,
                password=password
            )

            if user:
                login(request, user)
                return redirect('dashboard')

        return render(request, 'registration/login.html', {
            'error': 'Неправильний номер телефону або пароль.'
        })

    return render(request, 'registration/login.html')


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    return render(request, 'dashboard/admin.html')


def student_list_view(request):
    students = Student.objects.all()
    return render(request, 'core/student_list.html', {'students': students})


def branch_list_view(request):
    branches = Branch.objects.all()
    return render(request, 'core/branch_list.html', {'branches': branches})


def group_list_view(request):
    groups = StudentGroup.objects.all()
    return render(request, 'core/group_list.html', {'groups': groups})


def subject_list_view(request):
    subjects = Subject.objects.all()
    return render(request, 'core/subject_list.html', {'subjects': subjects})


def logout_view(request):
    logout(request)
    return redirect('login')

LOGIN_URL = 'login'