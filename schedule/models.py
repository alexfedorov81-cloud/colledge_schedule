from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from education.models import StudentGroup, Subject
from accounts.models import User
from django.utils import timezone
import datetime

class Building(models.Model):
    name = models.CharField(max_length=100, verbose_name='Учебный корпус')
    address = models.TextField()

    class Meta:
        verbose_name = 'Учебный корпус'
        verbose_name_plural = 'Учебные корпуса'

    def __str__(self):
        return self.name


class Classroom(models.Model):
    ROOM_TYPE_CHOICES = (
        ('lecture', 'Лекционная большая'),
        ('stand', 'Стандартная'),
        ('IT class', 'Кабинет IT'),
    )

    name = models.CharField(max_length=20)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    capacity = models.IntegerField()
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)

    class Meta:
        verbose_name = 'Аудитория'
        verbose_name_plural = 'Аудитории'

    def __str__(self):
        return f"{self.building.name}, ауд. {self.name}"


class TimeSlot(models.Model):
    order = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Пара'
        verbose_name_plural = 'Пары'

    def __str__(self):
        return self.name


class WeekType(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)

    class Meta:
        verbose_name = 'Неделя'
        verbose_name_plural = 'Недели'

    def __str__(self):
        return self.name


class StudyWeek(models.Model):
    """Модель для учебной недели"""
    start_date = models.DateField(unique=True)  # Понедельник недели
    end_date = models.DateField()  # Воскресенье недели
    week_number = models.IntegerField()  # Номер недели в семестре
    is_current = models.BooleanField(default=False)  # Текущая неделя
    is_published = models.BooleanField(default=False)  # Опубликовано ли расписание

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return f"Неделя {self.week_number} ({self.start_date} - {self.end_date})"

    def save(self, *args, **kwargs):
        # Автоматически вычисляем конец недели
        if self.start_date and not self.end_date:
            self.end_date = self.start_date + datetime.timedelta(days=6)
        super().save(*args, **kwargs)

    @classmethod
    def get_current_week(cls):
        """Получить текущую учебную неделю по дате"""
        today = timezone.now().date()
        try:
            return cls.objects.get(
                start_date__lte=today,
                end_date__gte=today
            )
        except cls.DoesNotExist:
            # Если нет недели для текущей даты, ищем ближайшую
            try:
                return cls.objects.filter(
                    start_date__gte=today
                ).order_by('start_date').first()
            except cls.DoesNotExist:
                return None

    @classmethod
    def update_current_week(cls):
        """Обновить флаг текущей недели на основе даты"""
        # Сбрасываем все флаги
        cls.objects.update(is_current=False)

        # Устанавливаем флаг для текущей недели
        current_week = cls.get_current_week()
        if current_week:
            current_week.is_current = True
            current_week.save()


class Schedule(models.Model):
    # Дни недели для choices
    DAYS_OF_WEEK = [
        (1, 'Понедельник'),
        (2, 'Вторник'),
        (3, 'Среда'),
        (4, 'Четверг'),
        (5, 'Пятница'),
        (6, 'Суббота'),
        (7, 'Воскресенье'),
    ]

    # Основные поля
    group = models.ForeignKey('education.StudentGroup', on_delete=models.CASCADE, verbose_name='Группа')
    teacher = models.ForeignKey('accounts.User', on_delete=models.CASCADE, verbose_name='Преподаватель')
    subject = models.ForeignKey('education.Subject', on_delete=models.CASCADE, verbose_name='Предмет')
    study_week = models.ForeignKey('StudyWeek', on_delete=models.CASCADE, verbose_name='Учебная неделя')

    # День недели с choices
    day_of_week = models.IntegerField(
        verbose_name='День недели',
        choices=DAYS_OF_WEEK
    )

    time_slot = models.ForeignKey('TimeSlot', on_delete=models.CASCADE, verbose_name='Время')
    classroom = models.ForeignKey('Classroom', on_delete=models.CASCADE, verbose_name='Аудитория')

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписания'

    def __str__(self):
        return f"{self.group} - {self.subject} - Неделя {self.study_week.week_number}"