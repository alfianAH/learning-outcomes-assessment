# Setup

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

    NEOSIA_API_TOKEN=

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


## Database Setup
1. Create database

    `CREATE DATABASE learning_outcomes_assessment;`

1. Create user

    `CREATE USER <POSTGRES_USER> WITH ENCRYPTED PASSWORD '<POSTGRES_PASSWORD>';`

1. Modifying parameters

    ```
    ALTER ROLE <POSTGRES_USER> SET client_encoding TO 'utf8';
    ALTER ROLE <POSTGRES_USER> SET default_transaction_isolation TO 'read committed';
    ALTER ROLE <POSTGRES_USER> SET timezone TO 'UTC';
    ALTER USER <POSTGRES_USER> CREATEDB;
    ```

1. Grant permission to the user

    `GRANT ALL PRIVILEGES ON DATABASE learning_outcomes_assessment TO <POSTGRES_USER>;`
