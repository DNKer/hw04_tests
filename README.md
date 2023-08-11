## [Тестирование проекта Yatube] (https://github.com/DNKer/hw03_forms "перейти к репозитарию проекта")

![workflow](https://github.com/DNKer/hw04_tests/actions/workflows/hw04_tests.yml/badge.svg?branch=master&event=push)

<img src="yatube\static\img\logo_tested.png" alt="drawing" width="250"/>

## Установка

Клонировать репозиторий и перейти в него в командной строке.

> приводятся команды для `Windows`.

Cоздать и активировать виртуальное окружение:
```bash
python -m venv venv
```

```bash
source venv/scripts/activate
```

Обновить систему управления пакетами:

```bash
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```bash
pip install -r requirements.txt
```

Выполнить миграции:

```bash
python manage.py makemigrations
```

```bash
python manage.py migrate
```

Запустить тесты, скачанные из репозитория (выполнять команду из директории: ``` hw04_tests$ ```):
```bash
pytest
```
Перейти в каталог:
```bash
cd yatube
```
и выполнить тесты, написанные в учебных целях для проекта:
```bash
python manage.py test
```