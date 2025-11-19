from django.shortcuts import render, get_object_or_404
from education.models import StudentGroup
from accounts.models import User
from schedule.models import Schedule, StudyWeek, TimeSlot
import datetime

def get_week_dates(week_offset=0):
    """Получить даты недели относительно текущей с учетом временной зоны"""
    # Используем timezone.now() для получения времени с учетом временной зоны
    today = datetime.timezone.now().date()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    target_week_start = start_of_week + datetime.timedelta(weeks=week_offset)
    target_week_end = target_week_start + datetime.timedelta(days=6)
    return target_week_start, target_week_end


def main_page(request):
    try:
        from education.models import StudentGroup
        from accounts.models import User
        groups = StudentGroup.objects.all().order_by('name')
        teachers = User.objects.filter(role='teacher').order_by('last_name')

        # Получаем текущую неделю
        current_week = StudyWeek.get_current_week()

    except ImportError:
        groups = []
        teachers = []
        current_week = None

    context = {
        'groups': groups,
        'teachers': teachers,
        'current_week': current_week,
    }
    return render(request, 'schedule/main.html', context)



def teacher_schedule(request, teacher_id, week_offset=0):
    """Расписание преподавателя с поддержкой недель"""
    teacher = get_object_or_404(User, id=teacher_id, role='teacher')

    # Получаем ВСЕ учебные недели
    available_weeks = StudyWeek.objects.all().order_by('start_date')

    # Определяем текущую неделю по дате
    current_week_by_date = StudyWeek.get_current_week()

    if not available_weeks.exists():
        context = {
            'teacher': teacher,
            'days': {},
            'current_week': None,
            'current_week_by_date': current_week_by_date,
            'week_start': None,
            'week_end': None,
            'week_offset': 0,
            'available_weeks': [],
            'has_previous': False,
            'has_next': False,
            'total_weeks': 0,
            'total_lessons': 0,
            'unique_groups': 0,
            'unique_subjects': 0,
        }
        return render(request, 'schedule/teacher_schedule.html', context)

    # Преобразуем week_offset в индекс недели
    week_index = int(week_offset)

    # Определяем, был ли запрос с явным week_offset
    request_path = request.path
    has_explicit_week = '/week/' in request_path

    if not has_explicit_week and current_week_by_date:
        # Запрос БЕЗ явного указания недели - показываем текущую по дате
        for idx, week in enumerate(available_weeks):
            if week == current_week_by_date:
                week_index = idx
                break
        else:
            future_weeks = available_weeks.filter(start_date__gte=current_week_by_date.start_date)
            if future_weeks.exists():
                week_index = list(available_weeks).index(future_weeks.first())
            else:
                week_index = available_weeks.count() - 1
    else:
        # Запрос С явным указанием недели - используем указанный week_offset
        pass

    # Проверяем границы
    if week_index < 0:
        week_index = 0
    elif week_index >= available_weeks.count():
        week_index = available_weeks.count() - 1

    # Берем неделю по индексу
    study_week = available_weeks[week_index]
    week_start = study_week.start_date
    week_end = study_week.end_date

    # ПРОСТО получаем расписание для преподавателя на выбранной неделе
    schedules = Schedule.objects.filter(
        teacher=teacher,
        study_week=study_week  # ← ПРОСТАЯ ФИЛЬТРАЦИЯ по неделе
    ).select_related(
        'group', 'subject', 'classroom', 'time_slot', 'study_week'
    ).order_by('day_of_week', 'time_slot__order')

    # Собираем расписание по дням и статистику
    days = {}
    total_lessons = 0
    groups_set = set()
    subjects_set = set()

    for schedule in schedules:
        day_num = schedule.day_of_week
        if day_num not in days:
            days[day_num] = []
        days[day_num].append(schedule)

        total_lessons += 1
        groups_set.add(schedule.group.id)
        subjects_set.add(schedule.subject.id)

    # Определяем доступность навигации
    has_previous = week_index > 0
    has_next = week_index < available_weeks.count() - 1

    context = {
        'teacher': teacher,
        'days': days,
        'current_week': study_week,
        'current_week_by_date': current_week_by_date,
        'week_start': week_start,
        'week_end': week_end,
        'week_offset': week_index,
        'available_weeks': available_weeks,
        'has_previous': has_previous,
        'has_next': has_next,
        'total_weeks': available_weeks.count(),
        'total_lessons': total_lessons,
        'unique_groups': len(groups_set),
        'unique_subjects': len(subjects_set),
        'week_type_display': 'четная' if study_week.week_number % 2 == 0 else 'нечетная',
    }
    return render(request, 'schedule/teacher_schedule.html', context)

def group_schedule(request, group_id, week_offset=0):
    """Расписание группы с поддержкой недель"""
    group = get_object_or_404(StudentGroup, id=group_id)

    # Получаем ВСЕ учебные недели
    available_weeks = StudyWeek.objects.all().order_by('start_date')

    # Определяем текущую неделю по дате
    current_week_by_date = StudyWeek.get_current_week()

    if not available_weeks.exists():
        context = {
            'group': group,
            'days': {},
            'current_week': None,
            'current_week_by_date': current_week_by_date,
            'week_start': None,
            'week_end': None,
            'week_offset': 0,
            'available_weeks': [],
            'has_previous': False,
            'has_next': False,
            'total_weeks': 0,
            'total_lessons': 0,
            'unique_teachers': 0,
            'unique_subjects': 0,
        }
        return render(request, 'schedule/group_schedule.html', context)

    # Преобразуем week_offset в индекс недели
    week_index = int(week_offset)

    # Определяем, был ли запрос с явным week_offset
    request_path = request.path
    has_explicit_week = '/week/' in request_path

    if not has_explicit_week and current_week_by_date:
        # Запрос БЕЗ явного указания недели (/group/2/) - показываем текущую по дате
        # Ищем индекс текущей недели по дате в available_weeks
        for idx, week in enumerate(available_weeks):
            if week == current_week_by_date:
                week_index = idx
                break
        # Если текущей недели по дате нет в available_weeks, используем ближайшую будущую
        else:
            future_weeks = available_weeks.filter(start_date__gte=current_week_by_date.start_date)
            if future_weeks.exists():
                week_index = list(available_weeks).index(future_weeks.first())
            else:
                week_index = available_weeks.count() - 1  # Последняя доступная неделя
    else:
        # Запрос С явным указанием недели (/group/2/week/X/) - используем указанный week_offset
        # Просто используем week_index как есть (уже преобразован из week_offset)
        pass

    # Проверяем границы
    if week_index < 0:
        week_index = 0
    elif week_index >= available_weeks.count():
        week_index = available_weeks.count() - 1

    # Берем неделю по индексу из available_weeks
    study_week = available_weeks[week_index]
    week_start = study_week.start_date
    week_end = study_week.end_date

    # Получаем расписание для выбранной недели
    schedules = Schedule.objects.filter(
        group=group,
        study_week=study_week
    ).select_related(
        'subject', 'teacher', 'classroom', 'time_slot', 'study_week'
    ).order_by('day_of_week', 'time_slot__order')

    # Собираем статистику
    days = {}
    total_lessons = 0
    teachers_set = set()
    subjects_set = set()

    for schedule in schedules:
        day_num = schedule.day_of_week
        if day_num not in days:
            days[day_num] = []
        days[day_num].append(schedule)

        total_lessons += 1
        teachers_set.add(schedule.teacher.id)
        subjects_set.add(schedule.subject.id)

    # Определяем доступность навигации
    has_previous = week_index > 0
    has_next = week_index < available_weeks.count() - 1

    context = {
        'group': group,
        'days': days,
        'current_week': study_week,
        'current_week_by_date': current_week_by_date,
        'week_start': week_start,
        'week_end': week_end,
        'week_offset': week_index,
        'available_weeks': available_weeks,
        'has_previous': has_previous,
        'has_next': has_next,
        'total_weeks': available_weeks.count(),
        'total_lessons': total_lessons,
        'unique_teachers': len(teachers_set),
        'unique_subjects': len(subjects_set),
        'week_type_display': 'четная' if study_week.week_number % 2 == 0 else 'нечетная',
    }
    return render(request, 'schedule/group_schedule.html', context)


def all_groups_schedule(request, week_offset=0):
    """Общее расписание всех групп на выбранной неделе"""
    # ... код получения available_weeks, study_week без изменений ...

    # Получаем ВСЕ группы (упорядоченные)
    groups = StudentGroup.objects.all().order_by('name')

    # Получаем ВСЕ временные слоты (упорядоченные)
    time_slots = TimeSlot.objects.all().order_by('order')

    # Получаем все расписания на выбранной неделе
    schedules = Schedule.objects.filter(
        study_week=study_week
    ).select_related(
        'group', 'subject', 'teacher', 'classroom', 'time_slot'
    )

    # Создаем структуру: days[day_num][time_slot_id][group_id] = занятия
    days = {}
    day_names = {
        1: 'Понедельник', 2: 'Вторник', 3: 'Среда',
        4: 'Четверг', 5: 'Пятница', 6: 'Суббота', 7: 'Воскресенье',
    }

    # Инициализируем структуру для всех дней, всех временных слотов и всех групп
    for day_num in range(1, 8):
        days[day_num] = {}
        for time_slot in time_slots:
            days[day_num][time_slot.id] = {}
            for group in groups:
                days[day_num][time_slot.id][group.id] = []

    # Заполняем данными
    for schedule in schedules:
        day_num = schedule.day_of_week
        time_slot_id = schedule.time_slot.id
        group_id = schedule.group.id

        if (day_num in days and
                time_slot_id in days[day_num] and
                group_id in days[day_num][time_slot_id]):
            days[day_num][time_slot_id][group_id].append(schedule)

    # Определяем доступность навигации
    has_previous = week_index > 0
    has_next = week_index < available_weeks.count() - 1

    context = {
        'days': days,
        'day_names': day_names,
        'groups': groups,
        'time_slots': time_slots,
        'current_week': study_week,
        'current_week_by_date': current_week_by_date,
        'week_start': week_start,
        'week_end': week_end,
        'week_offset': week_index,
        'available_weeks': available_weeks,
        'has_previous': has_previous,
        'has_next': has_next,
        'total_weeks': available_weeks.count(),
        'week_type_display': 'четная' if study_week.week_number % 2 == 0 else 'нечетная',
    }
    return render(request, 'schedule/all_groups_schedule.html', context)