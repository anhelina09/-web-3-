from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    Branch, Subject, Student, StudentGroup, 
    SubscriptionPlan, Lesson, Attendance, StudentSubscription
)

admin.site.register(Branch)
admin.site.register(Subject)
admin.site.register(Student)
admin.site.register(StudentGroup)
admin.site.register(SubscriptionPlan)
admin.site.register(Lesson)
admin.site.register(Attendance)
admin.site.register(StudentSubscription)