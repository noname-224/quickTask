# QuickTask

Телеграм-бот для управления задачами с поддержкой пошаговых сценариев (FSM), хранением состояния пользователя и работой с PostgreSQL.

---

## О проекте

Бот позволяет управлять списком задач прямо в Telegram:

* создавать задачи
* редактировать (название / описание / полностью)
* отмечать как выполненные
* удалять
* работать через inline-кнопки

---

## Технологии

* Python 3.13
* pyTelegramBotAPI
* SQLAlchemy (sync)
* PostgreSQL
* Docker / Docker Compose
* uv (dependency manager)

---

## Запуск через Docker

```bash
git clone https://github.com/noname-224/quickTask.git
cd quickTask

cp .env.example .env

docker compose up --build
```

---

## Переменные окружения

```env
BOT_TOKEN=your_telegram_bot_token

DB_HOST=postgres
DB_PORT=5432
DB_USER=postgres
DB_PASS=postgres
DB_NAME=quick_task
```

---