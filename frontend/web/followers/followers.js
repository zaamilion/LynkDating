document.addEventListener("DOMContentLoaded", function () {
    fetch('http://localhost:8002/get_follower', {
        method: 'GET',
        credentials: 'include' // если используешь куки для авторизации
    })
        .then(response => {
            if (response.status === 404) {
                const profileCard = document.getElementById('profile-card');
                const noProfileText = document.getElementById('no-profile');
                profileCard.style.display = 'none';
                noProfileText.style.display = 'block';
                return Promise.reject(new Error('No ankets'));

            }
            else if (response.status === 401) {
                window.location.href = '/'
            }
            return response.json();
        })
        .then(profile => {
            const profileCard = document.getElementById('profile-card');
            const noProfileText = document.getElementById('no-profile');
            profileCard.style.display = 'block';
            noProfileText.style.display = 'none';
            document.getElementById('profile-name').textContent = profile.name || 'Не указано';
            document.getElementById('profile-age').textContent = profile.age || 'Не указано';
            document.getElementById('profile-city').textContent = profile.city || 'Не указано';
            document.getElementById('profile-sex').textContent = profile.sex === true ? 'Мужской' : 'Женский';
            document.getElementById('profile-about').textContent = profile.description || 'Не указано';
            document.getElementById('avatar-preview').src = profile.avatar;
            document.getElementById('user_id').value = profile.user_id;

        })
        .catch(err => {
            console.error(err);
            document.querySelectorAll('.profile-info span:nth-child(2)').forEach(el => {
                el.textContent = 'Ошибка загрузки';
            });
        });
    // Обработка формы
    document.getElementById('like-button').addEventListener('click', function () {
        const payload = {
            user_id: parseInt(document.getElementById('user_id').value.trim())
        };

        fetch('http://localhost:8002/accept_follow', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload),
            credentials: "include"
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
        document.location.reload()
    });
    document.getElementById('dislike-button').addEventListener('click', function () {
        const payload = {
            user_id: parseInt(document.getElementById('user_id').value.trim())
        };
        fetch('http://localhost:8002/decline_follow', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload),
            credentials: "include"
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
        document.location.reload()
    });

});