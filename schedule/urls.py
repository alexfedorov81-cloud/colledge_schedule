from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
    path('all-groups/', views.all_groups_schedule, name='all_groups_schedule'),
    path('all-groups/week/<int:week_offset>/', views.all_groups_schedule, name='all_groups_schedule_week'),
    path('group/<int:group_id>/', views.group_schedule, name='group_schedule'),
    path('group/<int:group_id>/week/<int:week_offset>/', views.group_schedule, name='group_schedule_week'),
    path('teacher/<int:teacher_id>/', views.teacher_schedule, name='teacher_schedule'),
    path('teacher/<int:teacher_id>/week/<int:week_offset>/', views.teacher_schedule, name='teacher_schedule_week'),
]