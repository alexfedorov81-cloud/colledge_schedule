from django.contrib import admin
from .models import Institution, Faculty, Department, Specialization, StudentGroup, Subject


@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialization', 'course', 'start_year']
    list_filter = ['course', 'specialization__department__faculty']
    search_fields = ['name', 'specialization__name']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'total_hours', 'lecture_hours', 'practice_hours', 'lab_hours']
    list_filter = ['department']
    search_fields = ['name', 'code']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'code', 'department')
        }),
        ('Часы', {
            'fields': ('total_hours', 'lecture_hours', 'practice_hours', 'lab_hours')
        }),
    )


# Простая регистрация остальных моделей
admin.site.register(Institution)
admin.site.register(Faculty)
admin.site.register(Department)
admin.site.register(Specialization)
from django.contrib import admin

# Register your models here.
