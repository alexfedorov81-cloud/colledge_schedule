from django import forms
from django.core.exceptions import ValidationError
from .models import Schedule


class ScheduleAdminForm(forms.ModelForm):
    overwrite_existing = forms.BooleanField(
        required=False,
        initial=False,
        label='🗑️ УДАЛИТЬ конфликтующие занятия',
        help_text='Удалит ВСЕ занятия в это же время на этой неделе в этой аудитории'
    )

    class Meta:
        model = Schedule
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Сортируем queryset для лучшего отображения
        if 'study_week' in self.fields:
            self.fields['study_week'].queryset = self.fields['study_week'].queryset.order_by('start_date')

        # Прячем checkbox перезаписи при редактировании
        if self.instance.pk:
            self.fields['overwrite_existing'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()

        # Проверяем обязательные поля
        required_fields = ['study_week', 'day_of_week', 'time_slot', 'classroom']
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, 'Это поле обязательно для заполнения')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        overwrite_existing = self.cleaned_data.get('overwrite_existing', False)

        # ПРОСТАЯ И ЭФФЕКТИВНАЯ ЛОГИКА УДАЛЕНИЯ
        if overwrite_existing and not self.instance.pk:
            print("=== УДАЛЕНИЕ КОНФЛИКТУЮЩИХ ЗАНЯТИЙ ===")

            # Удаляем ВСЕ занятия с такими же параметрами
            deleted_count = Schedule.objects.filter(
                study_week=instance.study_week,
                day_of_week=instance.day_of_week,
                time_slot=instance.time_slot,
                classroom=instance.classroom
            ).delete()[0]

            print(f"✅ Удалено занятий: {deleted_count}")

        if commit:
            instance.save()

        return instance