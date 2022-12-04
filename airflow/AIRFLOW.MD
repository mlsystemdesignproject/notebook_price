Как установить airflow

Для начала нужно установить зависимости:
Можете установить Airflow через pipenv (pipenv install)

Также нужно установить переменные окружения:
Скопируйте файл .env.example -> .env и заполните значение для AIRFLOW_HOME

Инициализация airflow
```bash
airflow db init
```

Создание пользователя
```bash
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname Admin \
    --role Admin \
    --email enter@youremail.com
```

Запуск планировщика
```bash
airflow scheduler
```

Запуск веб-сервера
```bash
airflow webserver -p 8080
```
