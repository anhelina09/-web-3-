from django.db import models
from django.conf import settings
from .structure import Subject
from .people import Student, StudentGroup

class Lesson(models.Model):
    class LessonType(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', 'Individual'
        GROUP = 'GROUP', 'Group'

    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    lesson_type = models.CharField(max_length=15, choices=LessonType.choices, default=LessonType.GROUP)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='lessons')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lessons')
    
    # Якщо уроки групові — заповнюємо group. Якщо індивідуальні — заповнюємо student[cite: 161, 168].
    group = models.ForeignKey(StudentGroup, on_delete=models.CASCADE, related_name='lessons', blank=True, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='individual_lessons', blank=True, null=True)
    
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        target = self.group.name if self.lesson_type == self.LessonType.GROUP else f"{self.student}"
        return f"{self.date} [{self.start_time}-{self.end_time}] - {target}"


class LessonTemplate(models.Model):
    class LessonType(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', 'Individual'
        GROUP = 'GROUP', 'Group'

    lesson_type = models.CharField(max_length=15, choices=LessonType.choices, default=LessonType.GROUP)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    group = models.ForeignKey(StudentGroup, on_delete=models.CASCADE, blank=True, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True)
    
    day_of_week = models.IntegerField(choices=[(i, f"День {i}") for i in range(1, 8)])
    start_time = models.TimeField()
    end_time = models.TimeField()
    start_date = models.DateField(verbose_name="Період з")
    end_date = models.DateField(verbose_name="Період до")
    is_active = models.BooleanField(default=True)