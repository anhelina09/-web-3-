from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, time
from courses.models import Branch, Subject, Student, StudentGroup, Lesson, Attendance

User = get_user_model()

class EducationalCenterTests(APITestCase):

    def setUp(self):
        """Підготовка початкових даних для кожного тесту"""
        # 1. Створюємо філію
        self.branch = Branch.objects.create(
            name="Головна філія", address="вул. Шевченка 1", city="Львів"
        )
        
        # 2. Створюємо користувачів (Адміна та Вчителя) за нашою новою логікою (вхід за телефоном)
        self.admin_user = User.objects.create_superuser(
            phone="+380991111111", password="adminpassword123"
        )
        self.teacher = User.objects.create_user(
            phone="+380992222222", password="teacherpassword123", role="TEACHER"
        )
        
        # 3. Створюємо предмет
        self.subject = Subject.objects.create(
            name="Математика", branch=self.branch
        )
        
        # 4. Створюємо студента
        self.student = Student.objects.create(
            first_name="Олексій", last_name="Петренко", 
            phone="+380993333333", branch=self.branch
        )
        
        # 5. Створюємо групу та додаємо туди студента
        self.group = StudentGroup.objects.create(
            name="Група М-1", branch=self.branch, subject=self.subject, teacher=self.teacher
        )
        self.group.students.add(self.student)
        
        # Авторизуємо API-клієнт під Адміном, щоб мати права на створення об'єктів
        self.client.force_authenticate(user=self.admin_user)

    def test_user_creation(self):
        """1. Тест створення користувачів та перевірки їхніх ролей"""
        self.assertEqual(self.admin_user.phone, "+380991111111")
        self.assertEqual(self.admin_user.role, "ADMIN")
        self.assertTrue(self.admin_user.is_superuser)
        
        self.assertEqual(self.teacher.phone, "+380992222222")
        self.assertEqual(self.teacher.role, "TEACHER")
        self.assertFalse(self.teacher.is_superuser)

    def test_lesson_creation_and_conflict_prevention(self):
        """2. ТЕСТ КОНФЛІКТІВ РОЗКЛАДУ (Вимога Фази 2/3)"""
        url = "/api/lessons/"
        
        # Урок 1: Успішно створюємо перше заняття з 10:00 до 11:30
        lesson_data_1 = {
            "lesson_type": "GROUP",
            "subject": self.subject.id,
            "teacher": self.teacher.id,
            "group": self.group.id,
            "date": "2026-06-01",
            "start_time": "10:00:00",
            "end_time": "11:30:00",
            "status": "SCHEDULED"
        }
        response_1 = self.client.post(url, lesson_data_1, format='json')
        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)
        
        # Урок 2 (Конфліктний): Спроба створити уроки в той самий день з 11:00 до 12:00 для ТУГО Ж вчителя/групи
        # Час перетинається (11:00 < 11:30), система повинна заблокувати запит!
        lesson_data_conflict = {
            "lesson_type": "GROUP",
            "subject": self.subject.id,
            "teacher": self.teacher.id,
            "group": self.group.id,
            "date": "2026-06-01",
            "start_time": "11:00:00",
            "end_time": "12:00:00",
            "status": "SCHEDULED"
        }
        response_conflict = self.client.post(url, lesson_data_conflict, format='json')
        
        # Очікуємо помилку валідації (400 Bad Request)
        self.assertEqual(response_conflict.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Конфлікт", str(response_conflict.data))

        # Урок 3 (Едж-кейс): Створення уроку "встик" з 11:30 до 13:00. За ТЗ це НЕ конфлікт!
        lesson_data_edge = {
            "lesson_type": "GROUP",
            "subject": self.subject.id,
            "teacher": self.teacher.id,
            "group": self.group.id,
            "date": "2026-06-01",
            "start_time": "11:30:00",
            "end_time": "13:00:00",
            "status": "SCHEDULED"
        }
        response_edge = self.client.post(url, lesson_data_edge, format='json')
        self.assertEqual(response_edge.status_code, status.HTTP_201_CREATED)

    def test_attendance_marking_logic(self):
        """3. Тест логіки виставлення відвідуваності"""
        # Створюємо урок вручну через ORM
        lesson = Lesson.objects.create(
            lesson_type="GROUP", subject=self.subject, teacher=self.teacher,
            group=self.group, date=date(2026, 6, 1), 
            start_time=time(14, 0), end_time=time(15, 0)
        )
        
        url = "/api/attendance/"
        attendance_data = {
            "student": self.student.id,
            "lesson": lesson.id,
            "is_present": True,
            "notes": "Чудова робота на уроці"
        }
        
        response = self.client.post(url, attendance_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Attendance.objects.filter(student=self.student, lesson=lesson).exists())