document.addEventListener("DOMContentLoaded", function () {

    // === Загрузка данных профиля ===
    fetch('http://localhost:8020/get_my_anket', {
        method: 'GET',
        credentials: 'include'
    })
        .then(response => {
            if (response.status === 401) {
                window.location.href = '/';
            }
            return response.json();
        })
        .then(profile => {
            document.getElementById('name').value = profile.name || '';
            document.getElementById('age').value = profile.age || '';
            document.getElementById('location').value = profile.city || '';
            document.getElementById('lat').value = profile.lat;
            document.getElementById('lon').value = profile.lon;
            document.getElementById('avatarUrl').value = profile.avatar;
            document.getElementById('avatar-preview').src = profile.avatar;
            document.getElementById('tg').value = profile.telegram || '';
            if (profile.sex === true) {
                document.getElementById('male').checked = true;
            } else {
                document.getElementById('female').checked = true;
            }
            document.getElementById('about').value = profile.description || '';
        })
        .catch(err => {
            console.error(err);
        });

    // === Переменные для аватара и формы ===
    let debounceTimer;
    let selectedLocation = document.getElementById('location').value; // Храним правильное значение

    // === Инициализация Яндекс.Карт ===
    ymaps.ready(init);

    function init() {
        const input = document.getElementById('location');
        const suggestionsList = document.getElementById('suggestions-list');
        const selectedAddress = document.getElementById('selected-address');

        if (input && suggestionsList) {
            input.addEventListener('input', () => {
                const query = input.value.trim();
                if (!query) {
                    suggestionsList.style.display = 'none';
                    return;
                }

                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    ymaps.geocode(query, { suggest: true, results: 5 }).then(
                        result => {
                            const items = result.geoObjects.toArray();
                            suggestionsList.innerHTML = '';
                            suggestionsList.style.display = 'block';

                            if (items.length === 0) {
                                suggestionsList.innerHTML = '<li>Ничего не найдено</li>';
                                return;
                            }

                            items.forEach(item => {
                                const li = document.createElement('li');
                                li.textContent = item.properties.get('text');
                                li.style.padding = '10px';
                                li.style.cursor = 'pointer';
                                li.onclick = () => {
                                    const full_address = item.properties.get('text');
                                    const address = full_address.split(',').pop().trim();
                                    input.value = address;
                                    selectedLocation = address;
                                    selectedAddress.textContent = address;

                                    const coords = item.geometry.getCoordinates();
                                    const lat = parseFloat(coords[0].toFixed(6));
                                    const lon = parseFloat(coords[1].toFixed(6));

                                    document.getElementById('lat').value = lat;
                                    document.getElementById('lon').value = lon;

                                    suggestionsList.style.display = 'none';
                                };
                                suggestionsList.appendChild(li);
                            });
                        },
                        err => {
                            console.error('Ошибка геокодирования:', err);
                        }
                    );
                }, 500);
            });

            input.addEventListener('blur', () => {
                if (input.value && input.value !== selectedLocation) {
                    input.value = '';
                }
            });

            document.addEventListener('click', e => {
                if (!e.target.closest('#location') && !e.target.closest('#suggestions-list')) {
                    suggestionsList.style.display = 'none';
                }
            });
        }
    }

    // === Обработка аватара ===
    const avatarInput = document.getElementById('avatar');
    const avatarPreview = document.getElementById('avatar-preview');
    const avatarUrlInput = document.getElementById('avatarUrl');
    const profileForm = document.getElementById('profileForm');

    let uploadedAvatarUrl = document.getElementById('avatarUrl').value;

    if (avatarInput) {
        avatarInput.addEventListener('change', function () {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    avatarPreview.src = e.target.result;
                };
                reader.readAsDataURL(file);

                uploadAvatar(file);
            }
        });
    }

    function uploadAvatar(file) {
        const formData = new FormData();
        formData.append('file', file);

        fetch('http://localhost:8001/upload', {
            method: 'POST',
            body: formData,
            credentials: "include"

        })
            .then(response => response.json())
            .then(data => {
                if (data.url) {
                    uploadedAvatarUrl = data.url;
                    avatarPreview.src = data.url
                    if (avatarUrlInput) avatarUrlInput.value = uploadedAvatarUrl;
                }
            })
            .catch(error => {
                console.error('Ошибка загрузки аватара:', error);
            });
    }

    // === Отправка формы ===
    if (profileForm) {
        profileForm.addEventListener('submit', function (e) {
            e.preventDefault();

            // 1. Проверяем, идёт ли загрузка аватара
            if (avatarInput && avatarInput.files.length > 0 && !uploadedAvatarUrl) {
                alert('Подождите, аватар загружается...');
                return;
            }

            // 2. Собираем данные из формы
            const payload = {
                name: document.getElementById('name').value.trim(),
                age: parseInt(document.getElementById('age').value),
                city: document.getElementById('location').value.trim(),
                lat: parseFloat(document.getElementById('lat').value),
                lon: parseFloat(document.getElementById('lon').value),
                sex: document.getElementById('male').checked,
                sex_find: document.getElementById('find_male').checked,
                description: document.getElementById('about').value.trim(),
                telegram: document.getElementById('tg').value.trim(),
                avatar: document.getElementById('avatarUrl').value.trim() // Убираем пробелы
            };
            console.log(payload);
            // 5. Отправляем запрос
            fetch('http://localhost:8020/edit_anket', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },

                body: JSON.stringify(payload),
                credentials: "include" // если нужно сохранять сессию/куки
            })
                .then(response => {
                    if (response.ok) {
                        window.location.href = '/me'
                    }
                    return response.json();
                })
                .then(result => {
                    console.log('✅ Профиль успешно обновлён:', result);


                    // 7. Можно перенаправить или обновить страницу
                    // window.location.reload();
                })
                .catch(error => {
                    console.error('❌ Ошибка сохранения профиля:', error);
                    alert('Произошла ошибка при сохранении профиля.');
                });
        });
    }

});
document.getElementById('changeTgBtn').addEventListener('click', () => {
    document.querySelector('.tg-status').style.display = 'none';
    document.getElementById('codeForm').style.display = 'block';
});

document.getElementById('verifyCode').addEventListener('click', async () => {
    const code = document.getElementById('code').value.trim();
    const statusEl = document.getElementById('verificationStatus');
    const currentTgEl = document.getElementById('tg');

    if (!code || code.length !== 6) {
        statusEl.textContent = 'Код должен содержать ровно 6 символов.';
        statusEl.style.color = 'red';
        return;
    }

    const userId = document.getElementById('tg').value;

    try {
        const response = await fetch('http://localhost:8020/verificate_telegram', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code }),
            credentials: "include"
        });

        const result = await response.json();
        console.log(result)
        if (response.status === 200) {
            statusEl.textContent = '✅ Код успешно подтверждён!';
            statusEl.style.color = 'green';
            currentTgEl.value = result.id;

            // Возвращаем статус "подтверждён"
            const tgStatus = document.querySelector('.tg-status');
            tgStatus.style.display = 'flex';
            document.getElementById('codeForm').style.display = 'none';
        } else if (response.status === 400) {
            statusEl.textContent = '❌ Неверный код. Попробуйте снова.';
            statusEl.style.color = 'red';
        } else if (response.status === 409) {
            statusEl.textContent = '❌ Этот телеграм привязан к другому аккаунту';
            statusEl.style.color = 'red';
        }
    } catch (error) {
        console.error('Ошибка:', error);
        statusEl.textContent = '⚠️ Ошибка при проверке кода.';
        statusEl.style.color = '#d32f2f';
    }
});