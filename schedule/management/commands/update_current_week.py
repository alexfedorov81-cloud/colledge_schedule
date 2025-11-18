from django.core.management.base import BaseCommand
from schedule.models import StudyWeek


class Command(BaseCommand):
    help = 'Обновляет флаг текущей недели на основе текущей даты'

    def handle(self, *args, **options):
        StudyWeek.update_current_week()
        current_week = StudyWeek.get_current_week()

        if current_week:
            self.stdout.write(
                self.style.SUCCESS(f'Текущая неделя установлена: {current_week}')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Текущая неделя не найдена')
            )