from django.db import models
from .structure import Branch, Subject
from .people import Student

class SubscriptionPlan(models.Model):
    class PlanType(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', 'Individual'
        GROUP = 'GROUP', 'Group'

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        ARCHIVED = 'ARCHIVED', 'Archived'

    name = models.CharField(max_length=100)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='subscription_plans')
    plan_type = models.CharField(max_length=15, choices=PlanType.choices, default=PlanType.GROUP)
    subjects = models.ManyToManyField(Subject, related_name='subscription_plans')
    lessons_per_month = models.PositiveIntegerField(verbose_name="Занять на місяць")
    price_per_lesson = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна за один урок")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    def __str__(self):
        return f"{self.name} ({self.lessons_per_month} зан. -> ${self.price_per_lesson}/ур.)"


class StudentSubscription(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='subscriptions')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='student_subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateField(verbose_name="Дата початку підписки")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.student} - {self.subject.name} (Тариф: {self.plan.name})"