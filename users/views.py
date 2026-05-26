from django.shortcuts import render, redirect
from courses.models import Student, Branch, StudentGroup, Subject

def login_view(request):
    return redirect('dashboard')

def dashboard(request):
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
    return redirect('login')