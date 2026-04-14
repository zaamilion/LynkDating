async function renderMatches() {
    const container = document.getElementById('matchesList');

    try {
        const response = await fetch('http://localhost:8002/get_matches', {
            method: 'GET',
            credentials: 'include' // если используешь куки для авторизации
        });

        if (response.status === 403) {
            document.location.href = '/';
        }

        const matches = await response.json(); // Преобразуем ответ в JSON

        matches.forEach(user => {
            const matchHTML = `
                <div class="match-item">
                    <div class="avatar-container">
                        <img src="${user.avatar}" class="user-avatar" alt="${user.name}">
                    </div>
                    <div class="text-container">
                        <span class="username">${user.name}</span>
                        <span class="user-details">${user.age} лет, ${user.city}</span>
                        <a href="https://t.me/lynkdating_bot">Telegram</a>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', matchHTML);
        });

    } catch (error) {
        console.error('Ошибка при загрузке матчей:', error);
        container.innerHTML = '<p>Не удалось загрузить список совпадений.</p>';
    }
}

document.addEventListener('DOMContentLoaded', renderMatches);