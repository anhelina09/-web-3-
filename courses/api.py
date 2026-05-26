# courses/views.py або api.py
from rest_framework import viewsets
from .models import Branch, Student
from .serializers import BranchSerializer, StudentSerializer

class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer