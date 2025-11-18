// static/admin/js/schedule_conflicts.js
document.addEventListener('DOMContentLoaded', function() {
    const dayField = document.querySelector('#id_day_of_week');
    const timeField = document.querySelector('#id_time_slot');
    const classroomField = document.querySelector('#id_classroom');
    const teacherField = document.querySelector('#id_teacher');
    const groupField = document.querySelector('#id_group');
    const weekTypeField = document.querySelector('#id_week_type');

    function checkConflicts() {
        const day = dayField?.value;
        const time = timeField?.value;
        const classroom = classroomField?.value;
        const teacher = teacherField?.value;
        const group = groupField?.value;
        const weekType = weekTypeField?.value;

        if (day && time) {
            // Здесь можно добавить AJAX запрос для проверки конфликтов
            console.log('Checking conflicts...');
        }
    }

    // Слушаем изменения полей
    [dayField, timeField, classroomField, teacherField, groupField, weekTypeField].forEach(field => {
        if (field) {
            field.addEventListener('change', checkConflicts);
        }
    });
});