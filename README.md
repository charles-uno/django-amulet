# Django Amulet

The MTG deck [Amulet Titan][mtggoldfish] is known for its complex play patterns. 
This app presents users with sample opening hands, then shuffles the deck and solves for a sequence of plays to cast the titular Titan as quickly as possible. 
Think of it like flashcards: decide for yourself whether you would keep the hand, then play it out a few times to see what the numbers say!

The entire app is written in Python (using [Django][django]) for the sake of legibility and convenience.
There's also a bit of SCSS and JS to make things look presentable.
Content is mostly rendered on the server side and swapped onto the page via [htmx][htmx]. 
Requirements are handled by wrapping the app in a [Docker][docker] image (though `pipenv` or `virtualenv` would work too). 

This repo is a work in progress. 

## Running in Docker (Recommendeed)

The following instructions require Docker and `make`.

To launch the app on `localhost:8001`, use:
```
make run
```

To run a sanity check of the model *without* the Django web server, use:
```
make model
```

Unit tests are run during the build process, but the output is abbreviated. To see the full output:
```
make test
```

## Running Locally

These instructions are for running on your local machine. You must have `python3` installed (version 3.10 or newer), and you must install the requirements per:
```
pip3 install -r requirements.txt
```

To launch the app on `localhost:8000` use:
```
python3 amulet_flashcards/manage.py sass-compiler && python3 amulet_flashcards/manage.py runserver
```

To run the model *without* Django:
```
python3 -m amulet_flashcards.backend.amulet_model
```

To run the unit tests:
```
amulet_flashcards/backend/amulet_model/tests
```

## Ongoing Work

- Add nginx
- Implement game actions for Expedition Map
- Deploy to AWS via GitHub Actions
- Handle HTTPS
- Add a license (respecting WOTC fan content policy)
- Write up a blog post

[docker]: https://www.docker.com/
[mtggoldfish]: https://www.mtggoldfish.com/archetype/amulet-titan
[django]: https://www.djangoproject.com/
[github]: https://github.com/charles-uno/django-amulet
[blog]: https://charles.uno/amulet-simulation
[htmx]: https://htpx.org
