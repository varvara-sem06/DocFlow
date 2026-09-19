# DocFlow

AI-powered документооборот с согласованием и извлечением данных из файлов.

## Что умеет

- 📄 Загрузка документов (PDF, DOCX, JPG, PNG) с валидацией
- 🔐 JWT-аутентификация, изоляция данных по владельцу
- ✅ Workflow согласования: маршруты, шаги, история действий, email-уведомления
- 🤖 AI-пайплайн: OCR (Tesseract) → LLM-извлечение полей (Ollama / OpenAI)
- 🔍 Semantic search по документам через pgvector
- 📊 Аналитика: дашборд, timeline, топ-контрагенты, экспорт в Excel
- 🧪 Покрытие тестами бизнес-логики

## Стек

- **Backend:** Python 3.12, Django 5, DRF
- **Auth:** JWT (djangorestframework-simplejwt)
- **БД:** PostgreSQL 16 + pgvector
- **Очереди:** Celery + Redis
- **OCR:** Tesseract, pdfplumber, pdf2image
- **LLM:** Ollama (llama3.2) / OpenAI
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **Экспорт:** openpyxl
- **Тесты:** pytest, pytest-django, factory-boy

## Архитектура
[Client] → DRF API → Service Layer → Models
↓
Celery Tasks → OCR → LLM → Embeddings → pgvector
↓
Notifications (email/telegram)


## Быстрый старт

```bash
# 1. Клонировать
git clone <repo>
cd DocFlow

# 2. Виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Инфраструктура
brew install postgresql@16 pgvector redis tesseract poppler
brew services start postgresql@16
brew services start redis

createdb docflow
psql docflow -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 4. Настройки
cp .env.example .env  # отредактировать

# 5. Миграции
python manage.py migrate
python manage.py createsuperuser

# 6. Запуск (в трёх терминалах)
make run      # Django
make worker   # Celery
make beat     # Celery Beat

API

POST /api/token/ — получить JWT
GET /api/documents/ — список документов
POST /api/documents/ — загрузить документ (multipart)
GET /api/documents/{id}/ — детали
GET /api/documents/search_semantic/?q=... — semantic search
POST /api/routes/ — маршрут согласования
GET /api/requests/ — мои запросы
POST /api/requests/{id}/approve/ — согласовать шаг
POST /api/requests/{id}/reject/ — отклонить
GET /api/reports/dashboard/ — статистика
GET /api/reports/export/documents.xlsx — выгрузка
