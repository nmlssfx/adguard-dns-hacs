# AdGuard DNS Integration - Brands Files

Эти файлы предназначены для добавления интеграции AdGuard DNS в репозиторий [home-assistant/brands](https://github.com/home-assistant/brands).

## Структура файлов

```
brands/
└── adguard_dns/
    ├── domain.json    # Описание домена интеграции
    ├── logo.svg       # Логотип для HACS и документации
    └── icon.svg       # Иконка для интерфейса Home Assistant
```

## Инструкции по добавлению в brands

1. Форкните репозиторий [home-assistant/brands](https://github.com/home-assistant/brands)
2. Скопируйте папку `adguard_dns` в директорию `brands/` форкнутого репозитория
3. Создайте Pull Request с описанием:
   - Название: "Add AdGuard DNS integration"
   - Описание: "Adding brand assets for AdGuard DNS custom integration"

## Требования

- Все SVG файлы оптимизированы и не содержат внешних зависимостей
- `domain.json` содержит корректную информацию об интеграции
- Логотип и иконка соответствуют брендингу AdGuard

## Примечание

Добавление в brands репозиторий необходимо для прохождения валидации HACS и включения интеграции в список по умолчанию.