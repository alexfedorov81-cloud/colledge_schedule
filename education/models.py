from django.db import models
from django.conf import settings


class Institution(models.Model):
    name = models.CharField(max_length=200, verbose_name='Учебное заведение')
    short_name = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Учебное заведение'
        verbose_name_plural = '1. Учебные заведения'

    def __str__(self):
        return self.name


class Faculty(models.Model):
    name = models.CharField(max_length=200, verbose_name='Колледж')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Колледж'
        verbose_name_plural = '2. Колледжи'

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=200)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Отделение'
        verbose_name_plural = '3. Отделения'

    def __str__(self):
        return self.name


class Specialization(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Специальность'
        verbose_name_plural = '4. Специальности'

    def __str__(self):
        return self.name


class StudentGroup(models.Model):
    COURSE_CHOICES = [
        (1, '1 курс'),
        (2, '2 курс'),
        (3, '3 курс'),
        (4, '4 курс'),
        (5, '5 курс'),
        (6, '6 курс'),
    ]

    name = models.CharField(max_length=50)
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE)
    course = models.IntegerField(choices=COURSE_CHOICES)
    start_year = models.IntegerField()

    class Meta:
        verbose_name = 'Учебную группу'
        verbose_name_plural = '5. Учебные группы'

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, null=True, blank=True)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    total_hours = models.IntegerField(default=0)  # Общее количество часов
    lecture_hours = models.IntegerField(default=0)  # Часы лекций
    practice_hours = models.IntegerField(default=0)  # Часы практики
    lab_hours = models.IntegerField(default=0)  # Часы лабораторных

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = '6. Предмет'

    def __str__(self):
        return self.name

    def get_completed_hours(self, group):
        """Получить количество проведенных часов для группы"""
        from schedule.models import Schedule
        schedules = Schedule.objects.filter(
            group=group,
            subject=self
        )

        completed = {
            'lecture': 0,
            'practice': 0,
            'lab': 0,
            'total': 0
        }

        for schedule in schedules:
            # Предполагаем, что каждая пара - 2 академических часа
            hours = 2
            completed[schedule.lesson_type] += hours
            completed['total'] += hours

        return completed

    def get_remaining_hours(self, group):
        """Получить количество оставшихся часов для группы"""
        completed = self.get_completed_hours(group)

        return {
            'lecture': max(0, self.lecture_hours - completed['lecture']),
            'practice': max(0, self.practice_hours - completed['practice']),
            'lab': max(0, self.lab_hours - completed['lab']),
            'total': max(0, self.total_hours - completed['total'])
        }