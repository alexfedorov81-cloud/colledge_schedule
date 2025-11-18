document.addEventListener('DOMContentLoaded', function() {
    const weekTypeField = document.querySelector('#id_week_type');
    const specificWeekField = document.querySelector('#id_specific_week');
    const specificWeekRow = specificWeekField?.closest('.form-row');
    const excludedWeeksField = document.querySelector('#id_excluded_weeks');
    const excludedWeeksRow = excludedWeeksField?.closest('.form-row');

    function toggleWeekFields() {
        if (weekTypeField && specificWeekRow && excludedWeeksRow) {
            if (weekTypeField.value === 'single') {
                specificWeekRow.style.display = '';
                excludedWeeksRow.style.display = 'none';
            } else {
                specificWeekRow.style.display = 'none';
                excludedWeeksRow.style.display = '';
            }
        }
    }

    toggleWeekFields();
    weekTypeField?.addEventListener('change', toggleWeekFields);
});