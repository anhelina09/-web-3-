from django.db import models

class Branch(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        ARCHIVED = 'ARCHIVED', 'Archived'

    name = models.CharField(max_length=100, verbose_name="Назва філії")
    address = models.CharField(max_length=255, verbose_name="Адреса", blank=True, null=True)
    city = models.CharField(max_length=100, verbose_name="Місто", blank=True, null=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class Subject(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        ARCHIVED = 'ARCHIVED', 'Archived'

    name = models.CharField(max_length=100, verbose_name="Назва предмета")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='subjects')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        # ТЗ (Бізнес-правило 4.3): Унікальність назви предмета в межах однієї філії
        unique_together = ('name', 'branch')

    def __str__(self):
        return f"{self.name} - {self.branch.name}"