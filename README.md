# Learning Outcomes Assessment

## Project setup
1. Make virtual environment folder

    `python -m venv venv/`

1. Install packages

    `pip install -r requirements.txt`

1. Add environment variables (.env)

    ```
    DEBUG=

    DJANGO_ALLOWED_HOST=
    DJANGO_SECRET_KEY=

    POSTGRES_USER=
    POSTGRES_PASSWORD=
    ```

1. Install NPM packages from `package.json`

    `npm install`

1. Run Django migrations

    ```
    python manage.py makemigrations
    python manage.py migrate
    ```

1. Run Django project

    `python manage.py runserver`
