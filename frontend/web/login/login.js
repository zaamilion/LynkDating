document.addEventListener("DOMContentLoaded", function () {
    fetch('http://localhost:8000/verify', {
        method: 'POST',
        credentials: 'include'
    })
        .then(response => {
            if (response.ok) {
                window.location.href = '/me';

            } else {
                console.error('Ошибка проверки авторизации:', response.status);
            }
        })
        .catch(error => {
            console.error('Ошибка сети:', error);
        });

    const form = document.getElementById('loginForm');

    form.addEventListener('submit', async function (e) {
        e.preventDefault(); // Останавливаем стандартную отправку формы

        const formData = new FormData(form);
        const body = new URLSearchParams(formData).toString(); // Преобразуем в x-www-form-urlencoded
        try {
            const response = await fetch('http://localhost:8000/signin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                credentials: 'include', // Если используешь cookies для авторизации
                body: body
            });

            if (response.ok) {
                const result = await response.json();
                console.log('Успех:', result);

                // Перенаправление при успешном логине
                window.location.href = '/me';
            } else {
                const error = await response.json();
                alert(error.message || 'Ошибка входа');
            }
        } catch (err) {
            console.error('Сеть сломалась:', err);
            alert('Не удалось подключиться к серверу');
        }
    });
});