# Foodgram

Документация для API доступна по адресу:

```
https://62.113.108.216/api/docs/
```

![example workflow](https://github.com/Flomixon/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

## :books:Описание:
  Проект Foodgram  «Продуктовый помощник». Онлайн-сервис где пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## :satellite: Технологии: 

  - Python
  - Django REST Framework
  - API REST
  - Postman
  - Djoser
  - Doker

## :hammer_and_wrench: Как запустить проект:
 Скачайте на локальную машину или сервер данный репощиторий. В директории infra создайте файл .env и добавьте в него:
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER= #название БД
POSTGRES_PASSWORD= #пароль к БД
DB_HOST=db
DB_PORT=5432
SECRET_KEY= #секретный ключ конфигурации Django
Запустите сборку докер контейнеров командой

```
docker-compose up
```
