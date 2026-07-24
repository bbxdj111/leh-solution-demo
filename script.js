const translations = {
  ru: {
    title: "Создать новый заказ",
    subtitle: "Аккаунт не нужен! Просто введите ваши данные.",
    nameLabel: "Ваше имя *",
    namePlaceholder: "напр. Анна Шмидт",
    phoneLabel: "Номер телефона / WhatsApp *",
    addressLabel: "Адрес *",
    addressPlaceholder: "Берлин, Александерплац 3",
    serviceLabel: "Услуга *",
    optAcRepair: "❄️ Ремонт кондиционеров",
    optHeating: "🔥 Ремонт отопления",
    urgencyLabel: "Срочность *",
    optAsap: "🚨 Как можно скорее (аварийный случай)",
    optStandard: "📅 В течение недели",
    descLabel: "Описание проблемы",
    descPlaceholder: "Расскажите подробнее...",
    submitBtn: "Отправить заказ"
  },
  de: {
    title: "Neuen Auftrag erstellen",
    subtitle: "Kein Account nötig! Geben Sie einfach Ihre Daten ein.",
    nameLabel: "Ihr Name *",
    namePlaceholder: "z.B. Anna Schmidt",
    phoneLabel: "Telefonnummer / WhatsApp *",
    addressLabel: "Adresse *",
    addressPlaceholder: "Berlin, Alexanderplatz 3",
    serviceLabel: "Dienstleistung *",
    optAcRepair: "❄️ Klimaanlagen-Reparatur",
    optHeating: "🔥 Heizungs-Reparatur",
    urgencyLabel: "Dringlichkeit *",
    optAsap: "🚨 So schnell wie möglich (Notfall)",
    optStandard: "📅 Innerhalb einer Woche",
    descLabel: "Beschreibung des Problems",
    descPlaceholder: "Beschreiben Sie das Problem...",
    submitBtn: "Auftrag absenden"
  }
};

function setLanguage(lang) {
  // 1. Перевод текстов
  document.querySelectorAll('[data-i18n]').forEach(element => {
    const key = element.getAttribute('data-i18n');
    if (translations[lang] && translations[lang][key]) {
      element.textContent = translations[lang][key];
    }
  });

  // 2. Перевод подсказок (placeholder)
  document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
    const key = element.getAttribute('data-i18n-placeholder');
    if (translations[lang] && translations[lang][key]) {
      element.placeholder = translations[lang][key];
    }
  });

  // 3. Подсветка активной кнопки языка
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.remove('active');
    if (btn.getAttribute('onclick').includes(`'${lang}'`)) {
      btn.classList.add('active');
    }
  });

  // 4. Сохранение выбора
  localStorage.setItem('site_lang', lang);
}

function changeLanguage(lang) {
  setLanguage(lang);
}

// Запуск при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
  const savedLang = localStorage.getItem('site_lang') || 'ru';
  setLanguage(savedLang);
});