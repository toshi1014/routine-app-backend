# routine-app-backend

-   SNS Demo backend

-   Using _MySQL_(GPL) as database

-   Handle requests in REST API

## Setup

1.  Install lib by `pip3 install -r requirements.txt` in venv

2.  Config

    1.  Add env var in _config/config.txt_ or _config/secrets.txt_

        -   Variables needed are listed in _scripts/create_config_py.sh_

    2.  After `bash scripts/create_config_py.sh`, _config.py_ is generated

3.  Setup _MySQL_ container

    1.  Pull _MySQL_ image, and set password & port number

        e.g.

        ```
        docker run --name mysql -e MYSQL_ROOT_PASSWORD=password -d -p 3306:3306 -v "$(pwd)"/scripts:/root/ mysql
        ```

    2.  Create database & tables by `bash scripts/init_db.sh`

## Usage

1.  Start _MySQL_ container

2.  Launch server by `python3 manage.py runserver`
