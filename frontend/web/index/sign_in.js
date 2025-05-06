document.addEventListener("DOMContentLoaded", function () {
    fetch('http://localhost:8000/verify', {
        method: 'POST',
        credentials: 'include'
    })
        .then(response => {
            if (response.ok) {
                window.location.href = '/me';
            } else if (response.status === 401) {
                console.log('Пользователь не авторизован');
            } else {
                console.error('Ошибка проверки авторизации:', response.status);
            }
        })
        .catch(error => {
            console.error('Ошибка сети:', error);
        });


});
