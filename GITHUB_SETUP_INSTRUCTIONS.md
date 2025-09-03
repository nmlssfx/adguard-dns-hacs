# Инструкции по настройке GitHub репозитория

## Необходимые изменения для прохождения валидации HACS

Для успешного прохождения валидации HACS необходимо выполнить следующие шаги:

### 1. Добавить описание репозитория

1. Перейдите на страницу репозитория: https://github.com/nmlssfx/adguard-dns-hacs
2. Нажмите на иконку ⚙️ (Settings) справа от названия репозитория
3. В поле **Description** введите: `AdGuard DNS integration for Home Assistant`
4. Нажмите **Save changes**

### 2. Добавить топики (Topics)

1. На той же странице настроек найдите секцию **Topics**
2. Добавьте следующие топики (по одному):
   - `home-assistant`
   - `hacs`
   - `adguard-dns`
   - `integration`
3. Нажмите **Save changes**

### 3. Проверить настройки Issues

1. Убедитесь, что Issues включены (должна быть галочка возле **Issues**)
2. Если Issues отключены, включите их

### 4. Создать Pull Request в home-assistant/brands (опционально)

Для полного прохождения валидации HACS необходимо добавить интеграцию в репозиторий brands:

1. Форкните репозиторий: https://github.com/home-assistant/brands
2. Скопируйте папку `brands/adguard_dns/` из этого репозитория в форкнутый brands репозиторий
3. Создайте Pull Request с заголовком: "Add AdGuard DNS integration"

### 5. Проверить валидацию

После выполнения шагов 1-3:

1. Перейдите на вкладку **Actions** в репозитории
2. Запустите workflow "HACS Validation" заново
3. Проверьте, что все проверки проходят успешно

## Текущий статус

✅ **Выполнено:**
- Создана интеграция AdGuard DNS
- Настроены GitHub Actions
- Создан релиз v1.0.0
- Исправлен hacs.json
- Созданы файлы для brands репозитория

❌ **Требует выполнения:**
- Добавить описание репозитория
- Добавить топики репозитория
- (Опционально) Создать PR в home-assistant/brands

## Ожидаемый результат

После выполнения всех шагов валидация HACS должна показать:
- ✅ Validation description: passed
- ✅ Validation topics: passed
- ✅ Validation brands: passed (после добавления в brands)
- ✅ Все остальные проверки: passed

## Использование интеграции

После успешной валидации интеграцию можно будет установить через HACS:

1. Откройте HACS в Home Assistant
2. Перейдите в раздел "Integrations"
3. Нажмите "Explore & Download Repositories"
4. Найдите "AdGuard DNS" или добавьте репозиторий вручную: `https://github.com/nmlssfx/adguard-dns-hacs`
5. Установите интеграцию
6. Перезапустите Home Assistant
7. Добавьте интеграцию через Settings > Devices & Services

---

*Интеграция разработана совместно с **TraeAI Claude 4 Sonnet***