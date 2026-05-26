from django.db import models
from .people import Student
from .scheduling import Lesson

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='attendance_list')
    is_present = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True, verbose_name="Нотатки вчителя")

    class Meta:
        unique_together = ('student', 'lesson')

    def __str__(self):
        status = "Присутній" if self.is_present else "Відсутній"
        return f"{self.student} на уроці {self.lesson.date} - {status}"