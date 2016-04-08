# Email quark

## Setup

    brew install python3
    brew install postgresql
    brew service start postgresql

    python3 -m pip install py-postgresql
    createdb emailquark

## Running

    cp config.ini.example config.ini
    nano config.ini
    python3 email_to_json.py > email.list
    cat email.list | python3 json_to_postgres.py

## Links

 - [Homebrew](http://brew.sh/)
 - [Postico](https://eggerapps.at/postico/)
