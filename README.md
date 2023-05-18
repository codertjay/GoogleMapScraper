# GoogleMapScraper
# Getting Started

First clone the repository from GitHub and switch to the new directory:

    $ `git clone https://github.com/codertjay/GoogleMapScraper`
    $ `cd smsgpt`

Activate the virtualenv for your project.

Install project dependencies:

    $ `pip install -r requirements.txt`

Set Up your .env Just use the .env--sample provided to create yours

Then simply apply the migrations:

    $ `python manage.py migrate`

You can now run the development server:

    $` python manage.py runserver`

#### Run celery worker (On Windows only )

$` celery -A GoogleMapScraper  worker -l info --pool=solo`
######  On Mac
$  `celery -A GoogleMapScraper worker --loglevel=info`

##### And also the The .env File will contain 
`GOOGLE_MAP_API_KEY=GOOGLE_MAP_API_KEY`

`DEBUG=True`

`SECRET_KEY=SECRET_KEY
`

`POSTGRESDB_NAME=POSTGRESDB_NAME`

`POSTGRESDB_USER=POSTGRESDB_USER`

`POSTGRESDB_PASSWORD=POSTGRESDB_PASSWORD`

`POSTGRESDB_HOST=localhost`
