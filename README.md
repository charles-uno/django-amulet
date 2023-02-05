# Django Amulet

The MTG deck [Amulet Titan][mtggoldfish] is known for its complex play patterns. 
This app presents users with sample opening hands, then shuffles the deck and solves for a sequence of plays to cast the titular Titan as quickly as possible. 
Think of it like flashcards: decide for yourself whether you would keep the hand, then play it out a few times to see what the numbers say!

The app is written in Python using [Django][django] and [Gunicorn][gunicorn]. 
There's also a bit of SCSS and JS to make things look presentable.
Content is mostly rendered on the server side and swapped onto the page via [htmx][htmx]. 

Deployment uses [Docker][docker] and [GitHub Actions][github_actions]. 

NOTE: This repo is a work in progress

## Running in Docker (Recommendeed)

Build the app into a Docker container and launch on `localhost:8001`:
```
./scripts/launch-app.sh
```

## Running Locally

If you have Python 3.10 installed locally, you can run this code locally.

Install requirements:
```
pip3 install -r app/requirements.txt
```

To launch the app on `localhost:8000` use:
```
python3 app/manage.py sass-compiler
python3 app/manage.py runserver
```

To run the model on its own as a sanity check, without launching a web server:
```
python3 -m app.backend.amulet_model
```

To run the unit tests:
```
pytest app/backend/amulet_model/tests
```

## TODO

- Get nginx to serve static content so we can turn off Django debug mode
- Get the deck list to show up nicely on narrow screens
- Implement game actions for Expedition Map
- Handle HTTPS
- Handle the deck list on the front end? Currently using a sketchy `$DECKLIST` substitution instead of the template syntax
- Add a license (respecting WOTC fan content policy)
- Write up a blog post

[docker]: https://www.docker.com/
[gunicorn]: https://gunicorn.org/
[github_actions]: https://docs.github.com/en/actions
[mtggoldfish]: https://www.mtggoldfish.com/archetype/amulet-titan
[django]: https://www.djangoproject.com/
[github]: https://github.com/charles-uno/django-amulet
[blog]: https://charles.uno/amulet-simulation
[htmx]: https://htpx.org
