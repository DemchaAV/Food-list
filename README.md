# Food List

`Food List` - это внутреннее статическое PWA-приложение для Scott's Richmond. Оно работает как "Food Bible" для команды: помогает изучать блюда, быстро находить информацию по меню, сравнивать текущее и предыдущее меню и поддерживать данные в структурированном виде.

Архитектура проекта намеренно простая: без build step, без backend и без framework. Интерфейс собран из статических HTML-страниц с Tailwind через CDN и vanilla JavaScript, а данные меню загружаются из локальных JS-датасетов.

## Что умеет продукт

- Обучает команду описаниям блюд, винным рекомендациям, аллергенам, kitchen MEP и service MEP.
- Даёт мобильный каталог с поиском, фильтрами по категориям, детальной карточкой блюда и просмотром изображений.
- Позволяет переключаться между текущим и предыдущим меню в каталоге и тренажёре.
- Поддерживает редактирование меню прямо в браузере с экспортом обратно в формат данных репозитория.
- Работает как PWA: приложение можно установить, а основная оболочка кэшируется.

## Основные страницы

- `index.html` - домашняя страница и точка входа.
- `food_trainer.html` - режим обучения с карточками и quiz-сценариями.
- `mobile_food.html` - каталог меню, оптимизированный под быстрый просмотр на телефоне.
- `food_builder.html` - браузерный редактор карточек блюд с экспортом в `scotts.js`.

## Как устроен проект

Фронтенд загружает данные меню через `data/loader.js`. Этот файл подключает скрипты с меню, собирает текущие и предыдущие позиции и отправляет событие `foodLoaded`, когда данные готовы.

Контракты данных:

- Текущее меню: `window.registerFoodCategory([...])`
- Предыдущее меню: `window.registerPreviousFoodCategory([...])`

Ключевые файлы данных:

- `data/categories/scotts.js` - текущий датасет меню.
- `data/categories/scotts_previous.js` - предыдущее меню.
- `data/categories/food.json` - JSON-представление / альтернативное зеркало данных.
- `data/categories/menu_images/` - изображения блюд для каталога и билдера.

PWA-файлы:

- `manifest.json` - метаданные приложения и версия.
- `sw.js` - service worker с версионируемым кэшем.

## Формат записи блюда

Каждое блюдо хранится как JavaScript-объект внутри `scotts.js`. Типичная запись выглядит так:

```js
{
  id: "gillardeau-fr-oyster0",
  name: "Gillardeau (FR)",
  subtitle: "six £38.00 / dozen £76.00",
  category: "Oysters",
  description: "The Gillardeau oyster itself is firm and full in the shell...",
  wineSuggestion: {
    name: "Ruinart Blanc de Blancs",
    notes: "Elegant, fresh and lively..."
  },
  glossary: [
    { term: "Gillardeau", definition: "..." }
  ],
  additionalNotes: "Pass/service notes",
  allergens: ["Molluscs", "Sulphur Dioxide/Sulphites"],
  kitchenMep: "Kitchen setup notes",
  serviceMep: "Front-of-house setup notes",
  image: "data/categories/menu_images/GILLARDEAU (FR) OYSTER.jpeg",
  tags: ["new"]
}
```

Важно:

- `tags: ["new"]` используется в тренажёре и каталоге для фильтрации новых блюд.
- Категории могут быть обычными разделами меню или разбивкой set lunch по подкатегориям.
- Каталог и тренажёр умеют переключаться между текущим и предыдущим меню.

## Быстрый старт

Запустите локальный сервер из корня проекта:

```powershell
python -m http.server 8080
```

Затем откройте:

```text
http://localhost:8080
```

Не используйте `file://`:

- регистрация service worker требует HTTP/HTTPS
- динамическая загрузка скриптов рассчитана на запускаемый сервер

## Работа с меню

Основной редактируемый датасет в репозитории:

```text
data/categories/scotts.js
```

Рекомендуемый сценарий:

1. Откройте `food_builder.html`.
2. Измените существующие блюда или добавьте новые через интерфейс.
3. Экспортируйте результат в `scotts.js`.
4. Замените `data/categories/scotts.js` экспортированным файлом.
5. Запустите валидацию перед коммитом.

Важные особенности билдера:

- `food_builder.html` хранит рабочую копию в браузерном `localStorage` под ключом `foodItems`.
- Если билдер показывает устаревшие данные, очистите этот ключ или заново подтяните рабочую копию из репозитория.
- Изменения, сделанные в браузере, не попадают в репозиторий, пока вы не экспортируете файл и не замените `data/categories/scotts.js`.

## Обновление аллергенов

В проекте есть полуавтоматический сценарий синхронизации аллергенов.

1. Соберите данные по аллергенам из `viewthe.menu`:

```powershell
python scripts/data/scrape_viewthemenu_allergens.py --url https://viewthe.menu/dbav --out data/viewthemenu_allergens.json
```

2. Синхронизируйте собранные аллергены в локальные файлы меню:

```powershell
python scripts/data/sync_allergens_from_scraped.py
```

3. Проверьте исключения, требующие ручной проверки:

```text
data/allergen_sync_exceptions.json
```

## Валидация

После обновления данных запустите:

```powershell
python scripts/validation/validate_scotts.py
python scripts/validation/validate_scotts_full.py
python scripts/validation/verify_allergens.py
```

После этого вручную проверьте:

- `food_trainer.html`
- `mobile_food.html`
- `food_builder.html`

Особенно проверьте:

- корректную загрузку блюд
- переключение между текущим и предыдущим меню
- фильтрацию по новым блюдам
- отображение изображений
- аллергенные теги и детальные карточки
- экспорт из билдера

## Структура проекта

```text
.
|-- index.html
|-- food_trainer.html
|-- mobile_food.html
|-- food_builder.html
|-- manifest.json
|-- sw.js
|-- data/
|   |-- loader.js
|   |-- categories/
|   |   |-- scotts.js
|   |   |-- scotts_previous.js
|   |   |-- food.json
|   |   `-- menu_images/
|   |-- allergen_sync_exceptions.json
|   `-- viewthemenu_allergens.json
|-- scripts/
|   |-- data/
|   |-- images/
|   |-- validation/
|   `-- migrations/
`-- docs/
    `-- source-assets/
```

## Скрипты и обслуживание

- `scripts/data/` - сбор данных, cleanup, нормализация glossary, синхронизация аллергенов.
- `scripts/images/` - сопоставление изображений, AI-генерация картинок, извлечение из PDF.
- `scripts/validation/` - проверка структуры и содержимого меню.
- `scripts/migrations/` - разовые исторические скрипты обновления меню.

Исторические миграционные скрипты стоит пересматривать перед повторным запуском: в них могут быть жёстко зашиты предположения под конкретное обновление меню.

## Требования

Для веб-приложения:

- любой современный браузер
- интернет на первом запуске для загрузки Tailwind и шрифтов с CDN

Для служебных скриптов:

- Python 3.10+
- опционально `requests`
- опционально `PyMuPDF`
- опционально `OPENAI_API_KEY` для скриптов генерации изображений

Пример установки:

```powershell
pip install requests PyMuPDF
```

## Кэш и диагностика

- Service worker использует версионируемый кэш на основе `manifest.json`.
- После изменения фронтенда или данных меню сделайте hard refresh, если браузер продолжает показывать старую версию.
- Если страницы ведут себя по-разному, проверьте, что `manifest.json`, `sw.js` и файлы данных синхронизированы.
- Если страница открывается без данных, проверьте, что `data/loader.js` по-прежнему загружает и `scotts.js`, и `scotts_previous.js`.

## Кратко

`Food List` - это лёгкий статический продукт для обучения по меню и сопровождения меню. Его ценность в том, что операционные знания собраны в одном месте: описания блюд, винные рекомендации, аллергены, MEP-заметки и изображения доступны через быстрый внутренний интерфейс без backend и без build-пайплайна.
