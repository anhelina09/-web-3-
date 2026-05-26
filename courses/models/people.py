from django.db import models
from django.conf import settings
from .structure import Branch, Subject

class Student(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        ARCHIVED = 'ARCHIVED', 'Archived'

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='students')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    # Контакти батьків / опікунів за ТЗ (Пункт 4.4)
    parent_name = models.CharField(max_length=100, blank=True, null=True)
    parent_phone = models.CharField(max_length=20, blank=True, null=True)
    parent_email = models.EmailField(blank=True, null=True)
    parent_relationship = models.CharField(max_length=50, blank=True, null=True, verbose_name="Родинний зв'язок")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class StudentGroup(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        ARCHIVED = 'ARCHIVED', 'Archived'

    name = models.CharField(max_length=100)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='groups')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='groups')
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='teaching_groups'
    )
    students = models.ManyToManyField(Student, related_name='student_groups', blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    def __str__(self):
        return f"{self.name} ({self.branch.name})"