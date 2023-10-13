
## About the Model

The MTG deck [Amulet Titan][mtggoldfish] is known for its complex play patterns. 
This app presents users with sample opening hands, then shuffles the deck and solves for a sequence of plays to cast the titular [[Primeval Titan|Titan]] as quickly as possible. 
Think of it like flashcards: decide for yourself whether you would keep the hand, then play it out a few times to see what the numbers say!

Sequencing is determined via exhaustive search.
For example, an experienced player can generally eyeball whether to choose land or nonland for [[Abundant Harvest]], but spelling out the logic explicitly for the computer is tedious and fragile.
Instead of worrying about strategy and synergy, the computer makes two copies of the game.
The first chooses land, the second chooses nonland, and they proceed independently from there.
If either copy ends up casting turn-three [[Primeval Titan]] down the line, it's pretty safe to say that a human player could have done so as well.

You can read more about the model (and its applications) in my [previous write-up][blog]. 

## The Deck List

The model uses the list below. 
Note that [[Cavern of Souls]] and [[Vesuva]] are swapped out for other lands due to complexity.
The numbers and play patterns are still pretty much the same.

$DECKLIST

## Implementation

This app is written in Python using [Django][django] and [Gunicorn][gunicorn].
Content is rendered on the server side then swapped in using [htmx][htmx]. 
There's also a bit of SCSS and JS to make it look presentable.

Code is deployed to [AWS][aws] via [GitHub Actions][github_actions], where it runs in [Docker][docker] behind an [Nginx][nginx] proxy.
You can check out the code (game logic, web framework, and deployment) on [GitHub][github_source]. 

[aws]: https://aws.amazon.com/lightsail/
[blog]: https://charles.uno/amulet-simulation
[django]: https://www.djangoproject.com/
[docker]: https://www.docker.com/
[github_actions]: https://docs.github.com/en/actions
[github_source]: https://github.com/charles-uno/django-amulet
[gunicorn]: https://gunicorn.org/
[htmx]: https://htpx.org
[mtggoldfish]: https://www.mtggoldfish.com/archetype/amulet-titan
[nginx]: https://www.nginx.com/