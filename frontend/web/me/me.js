document.addEventListener("DOMContentLoaded", function () {
    fetch('http://localhost:8020/get_my_anket', {
        method: 'GET',
        credentials: 'include' // если используешь куки для авторизации
    })
        .then(response => {
            if (response.status === 404) {
                window.location.href = '/create_anket';
            }
            else if (response.status === 401) {
                window.location.href = '/'
            }
            else if (!response.ok) {
                throw new Error('Ошибка загрузки профиля');
            }
            return response.json();
        })
        .then(profile => {
            document.getElementById('profile-name').textContent = profile.name || 'Не указано';
            document.getElementById('profile-age').textContent = profile.age || 'Не указано';
            document.getElementById('profile-city').textContent = profile.city || 'Не указано';
            document.getElementById('profile-sex').textContent = profile.sex === true ? 'Мужской' : 'Женский';
            document.getElementById('profile-about').textContent = profile.description || 'Не указано';
            document.getElementById('avatar-preview').src = profile.avatar;
        })
        .catch(err => {
            console.error(err);
            document.querySelectorAll('.profile-info span:nth-child(2)').forEach(el => {
                el.textContent = 'Ошибка загрузки';
            });
        });
    // Обработка формы
    const form = document.querySelector('form');

    if (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault(); // ✅ Теперь e передан правильно

            fetch('http://localhost:8000/logout', {
                method: 'POST',
                credentials: 'include'
            })
                .then(response => {
                    if (response.ok) {
                        window.location.href = '/';
                    } else {
                        console.error('Ошибка выхода:', response.status);
                    }
                })
                .catch(error => {
                    console.error('Ошибка сети:', error);
                });
        });
    }
});