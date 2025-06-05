.PHONY: help install test test-unit test-api test-integration coverage lint format clean

# По умолчанию показываем help
help:
	@echo "TelecomBackend - Команды для разработки"
	@echo ""
	@echo "Установка и настройка:"
	@echo "  install          Установка всех зависимостей"
	@echo "  install-dev      Установка с dev зависимостями"
	@echo ""
	@echo "Тестирование:"
	@echo "  test            Запуск всех тестов"
	@echo "  test-unit       Запуск только unit тестов"
	@echo "  test-api        Запуск только API тестов"
	@echo "  test-models     Запуск только тестов моделей"
	@echo "  test-fast       Быстрые тесты (без coverage)"
	@echo "  coverage        Запуск тестов с покрытием"
	@echo "  coverage-html   Генерация HTML отчета покрытия"
	@echo ""
	@echo "Качество кода:"
	@echo "  lint            Проверка стиля кода"
	@echo "  format          Автоформатирование кода"
	@echo "  check           Полная проверка качества"
	@echo ""
	@echo "Разработка:"
	@echo "  migrate         Применение миграций"
	@echo "  makemigrations  Создание миграций"
	@echo "  runserver       Запуск dev сервера"
	@echo "  shell           Django shell"
	@echo "  clean           Очистка временных файлов"

# Установка зависимостей
install:
	pip install -r requirements.txt

install-dev: install
	pip install pytest pytest-django pytest-cov factory-boy faker freezegun responses
	pip install black flake8 isort coverage

# Тестирование
test:
	python -m pytest --verbose --tb=short

test-unit:
	python -m pytest -m unit --verbose

test-api:
	python -m pytest -m api --verbose

test-models:
	python -m pytest -m model --verbose

test-fast:
	python -m pytest --no-cov --verbose --tb=short

# Покрытие тестами
coverage:
	python -m pytest --cov=equipment --cov=authentication --cov=telecom_backend
	coverage report --show-missing

coverage-html:
	python -m pytest --cov=equipment --cov=authentication --cov=telecom_backend --cov-report=html
	@echo "HTML отчет сохранен в htmlcov/index.html"

coverage-xml:
	python -m pytest --cov=equipment --cov=authentication --cov=telecom_backend --cov-report=xml

# Качество кода  
lint:
	flake8 equipment/ authentication/ telecom_backend/ tests/
	
format:
	black equipment/ authentication/ telecom_backend/ tests/
	isort equipment/ authentication/ telecom_backend/ tests/

check: lint test
	@echo "✅ Все проверки пройдены!"

# Django команды
migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

runserver:
	python manage.py runserver

shell:
	python manage.py shell

collectstatic:
	python manage.py collectstatic --noinput

# Создание тестовых данных
create-test-data:
	python manage.py create_test_data

# Очистка
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/

# Docker команды
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# CI/CD команды
ci-test: install-dev
	python -m pytest --cov=equipment --cov=authentication --cov=telecom_backend --cov-report=xml --cov-fail-under=95

ci-lint:
	flake8 equipment/ authentication/ telecom_backend/ tests/ --max-line-length=88 --extend-ignore=E203,W503

ci-format-check:
	black --check equipment/ authentication/ telecom_backend/ tests/
	isort --check-only equipment/ authentication/ telecom_backend/ tests/

# Полная проверка для CI
ci: ci-lint ci-format-check ci-test
	@echo "🎉 CI проверки пройдены!" 