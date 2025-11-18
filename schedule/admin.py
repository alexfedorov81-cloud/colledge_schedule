from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages  # ← ДОБАВЬТЕ ЭТОТ ИМПОРТ
from .models import Schedule, StudyWeek, Building, Classroom, TimeSlot
from .forms import ScheduleAdminForm


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'get_classroom_count']
    search_fields = ['name', 'address']
    list_per_page = 20

    def get_classroom_count(self, obj):
        return obj.classroom_set.count()

    get_classroom_count.short_description = 'Кол-во аудиторий'


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ['name', 'building', 'capacity', 'room_type']
    list_filter = ['building', 'room_type', 'capacity']
    search_fields = ['name', 'building__name']
    list_per_page = 30




@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['order', 'start_time', 'end_time', 'get_duration']
    ordering = ['order']
    list_per_page = 15

    def get_duration(self, obj):
        return f"{obj.start_time.strftime('%H:%M')} - {obj.end_time.strftime('%H:%M')}"

    get_duration.short_description = 'Время'

@admin.register(StudyWeek)
class StudyWeekAdmin(admin.ModelAdmin):
    list_display = ['week_number', 'start_date', 'end_date']
    list_filter = ['start_date']
    search_fields = ['week_number']
    ordering = ['start_date']

    fieldsets = (
        (None, {
            'fields': ('week_number', 'start_date', 'end_date')
        }),
    )


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    form = ScheduleAdminForm
    list_display = [
        'group',
        'teacher',
        'subject',
        'study_week',
        'get_day_display',
        'time_slot',
        'classroom',
        'get_conflict_warning'
    ]
    list_filter = [
        'group',
        'teacher',
        'study_week',
        'day_of_week',
        'time_slot'
    ]
    search_fields = [
        'group__name',
        'teacher__username',
        'teacher__first_name',
        'teacher__last_name',
        'subject__name'
    ]
    list_per_page = 50

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'group',
                'teacher',
                'subject',
                'study_week'
            )
        }),
        ('Время и место', {
            'fields': (
                'day_of_week',
                'time_slot',
                'classroom',
                'overwrite_existing'
            )
        }),
    )

    def get_day_display(self, obj):
        """Красивое отображение дня недели"""
        return obj.get_day_of_week_display()

    get_day_display.short_description = 'День недели'
    get_day_display.admin_order_field = 'day_of_week'

    def get_conflict_warning(self, obj):
        """Показывает предупреждение о конфликтах"""
        conflicts = Schedule.objects.filter(
            study_week=obj.study_week,
            day_of_week=obj.day_of_week,
            time_slot=obj.time_slot,
            classroom=obj.classroom
        ).exclude(id=obj.id)

        if conflicts.exists():
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ Конфликт</span>'
            )
        return format_html('<span style="color: green;">✓ OK</span>')

    get_conflict_warning.short_description = 'Статус'

    def save_model(self, request, obj, form, change):
        """Дополнительные действия при сохранении"""
        overwrite_existing = form.cleaned_data.get('overwrite_existing', False)

        try:
            super().save_model(request, obj, form, change)

            if overwrite_existing and not change:
                messages.success(
                    request,
                    'Занятие добавлено с перезаписью конфликтующих занятий'
                )
            elif change:
                messages.success(request, 'Занятие обновлено')
            else:
                messages.success(request, 'Занятие добавлено')

        except Exception as e:
            # УБЕРИТЕ from django.contrib import messages отсюда
            messages.error(request, f'Ошибка сохранения: {e}')