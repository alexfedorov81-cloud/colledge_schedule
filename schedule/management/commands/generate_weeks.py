from django.core.management.base import BaseCommand
from django.utils import timezone
from schedule.models import StudyWeek
import datetime


class Command(BaseCommand):
    help = 'Генерирует учебные недели на семестр для Новосибирска'

    def add_arguments(self, parser):
        parser.add_argument('start_date', type=str, help='Дата начала семестра (ГГГГ-ММ-ДД)')
        parser.add_argument('weeks', type=int, help='Количество недель в семестре')

    def handle(self, *args, **options):
        start_date = datetime.datetime.strptime(options['start_date'], '%Y-%m-%d').date()
        weeks_count = options['weeks']

        # Удаляем старые недели
        StudyWeek.objects.all().delete()

        for week_num in range(1, weeks_count + 1):
            week_start = start_date + datetime.timedelta(weeks=week_num - 1)
            week_end = week_start + datetime.timedelta(days=6)

            StudyWeek.objects.create(
                start_date=week_start,
                end_date=week_end,
                week_number=week_num,
                is_current=(week_num == 1),  # Первая неделя - текущая
                is_published=True
            )
            self.stdout.write(f'Создана неделя {week_num}: {week_start} - {week_end}')

        self.stdout.write(
            self.style.SUCCESS(f'Успешно создано {weeks_count} учебных недель для Новосибирска')
        )