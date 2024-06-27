// Скрипт для работы фильтров
document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById('filters-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();  // Предотвратить стандартную отправку формы

        const urlParams = new URLSearchParams(window.location.search);
        const inputs = form.querySelectorAll('input[type="number"], input[type="text"], input[type="checkbox"]');

        // Очищаем все параметры магазинов перед добавлением новых
        urlParams.delete('shop_id');
        // Удаление параметра page, чтобы сбросить пагинацию
        urlParams.delete('page');

        inputs.forEach(input => {
            if (input.type === 'checkbox') {
                if (input.checked) {
                    urlParams.append(input.name, input.value);  // Добавляем выбранные значения
                }
            } else if (input.value !== '') {
                urlParams.set(input.name, input.value);  // Устанавливаем или обновляем значения для других полей
            } else {
                urlParams.delete(input.name);  // Удаляем параметр если поле пустое
            }
        });

        // Обновить URL
        window.location.search = urlParams.toString();
    });
});

// Скрипт для работы кнопок сортировки
document.addEventListener("DOMContentLoaded", function() {
    const buttons = document.querySelectorAll('.sort-button');
    const urlParams = new URLSearchParams(window.location.search);

    // Установка активного состояния кнопок
    buttons.forEach(button => {
        if (urlParams.get('product_sort') === button.dataset.sort) {
            button.classList.add('active');
            button.classList.remove('btn-outline-secondary');
            button.classList.add('btn-secondary');
        }
    });

    // Добавление события клика и отправка формы
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            urlParams.set('product_sort', this.dataset.sort);
            window.location.search = urlParams.toString();
        });
    });
});
