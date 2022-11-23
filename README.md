# recipe-api
Recipe API project in django.

# How to run App
```
docker-compose up
````

Swagger (http://localhost:8000/api/docs/)

# How to run tests
```
docker-compose run --rm app sh -c "python manage.py test"
```

# How to run lint
```
docker-compose run --rm app sh -c "flake8"
```
