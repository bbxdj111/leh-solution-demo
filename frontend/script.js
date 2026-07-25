// --- 1. Геолокация мастера в реальном времени ---
function initGeoTracking() {
    if (!("geolocation" in navigator)) {
        console.warn("Геолокация не поддерживается вашим браузером");
        return;
    }

    // Отслеживаем координаты раз в 30 секунд или при перемещении
    navigator.geolocation.watchPosition(
        (position) => {
            const coords = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                timestamp: new Date().toISOString()
            };
            
            console.log("📍 Геолокация обновлена:", coords);
            sendOrQueueData('/api/geo/track', coords);
        },
        (error) => console.error("Ошибка получения GPS:", error.message),
        { enableHighAccuracy: true, timeout: 15000, maximumAge: 30000 }
    );
}

// --- 2. Оффлайн-очередь (Offline Sync Queue) ---
function sendOrQueueData(url, payload) {
    if (navigator.onLine) {
        // Если сеть есть — отправляем на сервер напрямую
        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        }).catch(() => saveToOfflineQueue(url, payload));
    } else {
        // Если сети нет — сохраняем в оффлайн-накопитель
        saveToOfflineQueue(url, payload);
    }
}

function saveToOfflineQueue(url, payload) {
    let queue = JSON.parse(localStorage.getItem('offline_queue') || '[]');
    queue.push({ url, payload, timestamp: new Date().toISOString() });
    localStorage.setItem('offline_queue', JSON.stringify(queue));
    updateConnectionStatusUI(false);
}

// --- 3. Автоматическая синхронизация при появлении сети ---
async function syncOfflineData() {
    let queue = JSON.parse(localStorage.getItem('offline_queue') || '[]');
    if (queue.length === 0) return;

    console.log(`🔄 Синхронизация: отправка ${queue.length} оффлайн-записей...`);
    
    let remainingQueue = [];
    for (const item of queue) {
        try {
            await fetch(item.url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(item.payload)
            });
        } catch (err) {
            // Если всё ещё нет связи, оставляем в очереди
            remainingQueue.push(item);
        }
    }

    localStorage.setItem('offline_queue', JSON.stringify(remainingQueue));
    if (remainingQueue.length === 0) {
        console.log("✅ Все оффлайн-данные успешно синхронизированы!");
    }
}

// Отслеживаем статус сети (Online / Offline)
function updateConnectionStatusUI(isOnline) {
    const statusEl = document.getElementById('network-status');
    if (!statusEl) return;
    
    if (isOnline) {
        statusEl.textContent = 'Онлайн';
        statusEl.className = 'bg-emerald-500/10 text-emerald-400 text-xs px-2.5 py-1 rounded-full border border-emerald-500/20';
    } else {
        statusEl.textContent = 'Оффлайн (Режим сохранения)';
        statusEl.className = 'bg-amber-500/10 text-amber-400 text-xs px-2.5 py-1 rounded-full border border-amber-500/20';
    }
}

window.addEventListener('online', () => {
    updateConnectionStatusUI(true);
    syncOfflineData();
});

window.addEventListener('offline', () => {
    updateConnectionStatusUI(false);
});

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    initGeoTracking();
    updateConnectionStatusUI(navigator.onLine);
});