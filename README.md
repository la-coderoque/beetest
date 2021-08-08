# beetest
Для старта:
```
docker-compose up
```
Внутрь контейнера копируется sqlite база с примененными миграциями, без записей 

# Примеры запросов
Админка доступна по /admin/

Список мероприятий:
```
curl --location --request GET 'http://127.0.0.1:5000/events/'
```
Детальная информация по мероприятию:
```
curl --location --request GET 'http://127.0.0.1:5000/events/1'
```
Регистрация пользователей:
```
curl --location --request PUT 'http://127.0.0.1:5000/events/registration/' \
--header 'Content-Type: application/json' \
--data-raw '{"event_id": 1, "users": [1, 2, 3]}'
```
