# Django Amulet

The MTG deck [Amulet Titan][mtggoldfish] is known for its complex play patterns. 
This app presents users with sample opening hands, then shuffles the deck and solves for a sequence of plays to cast the titular Titan as quickly as possible. 
Think of it like flashcards: decide for yourself whether you would keep the hand, then play it out a few times to see what the numbers say!

The app is written in Python using [Django][django] and [Gunicorn][gunicorn]. 
Content is rendered on the server side and swapped onto the page via [htmx][htmx]. 
There's also a bit of CSS and JS to make things look presentable.

Deployment is handled by [GitHub Actions][github_actions].
On commit, content is built into a [Docker][docker] container, copied over to [AWS][aws], and launched along with an Nginx proxy.

NOTE: This repo is a work in progress!

## Running in Docker (Recommendeed)

Build the app into a Docker container and launch on `localhost:8001`:
```
./scripts/launch-app.sh
```

## TODO

- fix slight zoom on mobile
- Get the deck list to show up nicely on narrow screens
- Implement game actions for Expedition Map
- Handle HTTPS
- Handle the deck list on the front end? Currently using a sketchy `$DECKLIST` substitution instead of the template syntax
- Add a license (respecting WOTC fan content policy)
- Write up a blog post

[aws]: https://aws.amazon.com/lightsail/
[blog]: https://charles.uno/amulet-simulation
[django]: https://www.djangoproject.com/
[docker]: https://www.docker.com/
[github_actions]: https://docs.github.com/en/actions
[github_source]: https://github.com/charles-uno/django-amulet
[gunicorn]: https://gunicorn.org/
[htmx]: https://htpx.org
[mtggoldfish]: https://www.mtggoldfish.com/archetype/amulet-titan
