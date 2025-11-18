/ Основные JavaScript функции для системы расписания
document.addEventListener('DOMContentLoaded', function() {
    // Плавная прокрутка
    const smoothScroll = (target) => {
        const element = document.querySelector(target);
        if (element) {
            element.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    };

    // Добавление анимаций при загрузке
    const animateElements = () => {
        const cards = document.querySelectorAll('.schedule-card, .main-card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('fade-in');
        });
    };

    // Подсветка текущего дня недели
    const highlightCurrentDay = () => {
        const today = new Date().getDay();
        // Преобразование: 0=воскресенье -> 7=воскресенье, 1=понедельник -> 1
        const adjustedDay = today === 0 ? 7 : today;

        const dayHeaders = document.querySelectorAll('.schedule-card .card-header');
        dayHeaders.forEach(header => {
            const dayText = header.textContent.trim().toLowerCase();
            const dayMap = {
                'понедельник': 1,
                'вторник': 2,
                'среда': 3,
                'четверг': 4,
                'пятница': 5,
                'суббота': 6,
                'воскресенье': 7
            };

            if (dayMap[dayText] === adjustedDay) {
                header.classList.add('bg-warning');
                header.classList.remove('bg-secondary');
            }
        });
    };

    // Инициализация
    animateElements();
    highlightCurrentDay();

    // Обработчики событий
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            smoothScroll(this.getAttribute('href'));
        });
    });

    // Toast уведомления (если понадобятся)
    window.showToast = function(message, type = 'info') {
        // Простая реализация toast уведомлений
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    };
});