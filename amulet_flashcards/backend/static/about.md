
## About the Model

The MTG deck [Amulet Titan][mtggoldfish] is known for its complex play patterns. 
This app presents users with sample opening hands, then shuffles the deck and solves for a sequence of plays to cast the titular [[Primeval Titan|Titan]] as quickly as possible. 
Think of it like flashcards: decide for yourself whether you would keep the hand, then play it out a few times to see what the numbers say!

Sequencing is determined via exhaustive search.
Whenever the computer is faced with a choice, it tries both options and keeps whichever works out best.
For example, an experienced player can generally eyeball whether to choose land or nonland for [[Abundant Harvest]], but spelling out the logic explicitly for the computer is tedious and fragile.
Instead of worrying about strategy and synergy, the computer splits the game into two copies.
The first chooses land, the second chooses nonland, and they proceed independently from there.
If either copy ends up casting turn-three [[Primeval Titan]] down the line, it's pretty safe to say that a human player could have done so as well.

Exhaustive search is straightforward and reliable, but also computationally expensive.
A few simplifications are made in the interest of performance.
Blue mana isn't tracked, so the model never transmutes [[Tolaria West]].
The color-fixing ability on [[Dryad of the Ilysian Grove]] is ignored.
And [[Cavern of Souls]] and [[Vesuva]] are swapped for less-complex lands.
These changes have minimal impact on the model's play patterns and numbers.

That said, please don't expect this model to teach you good sequencing!
If it's possible to cast [[Primeval Titan]] (or [[Cultivator Colossus]]) by turn three, it's guaranteed to find a way to do so.
But in a real game, you also need to worry about developing your mana, playing around interaction, and paying for your [[Summoner's Pact|Pact]] on turn four.
Consider this a starting point, not an authority.


## The Deck List

The model uses the list below. 
As mentioned above, [[Cavern of Souls]] and [[Vesuva]] are omitted out due to complexity.
The numbers and play patterns are still pretty much the same.

$DECKLIST

TODO: [[Radiant Fountain]], [[Slayers' Stronghold]] and [[Sunhome, Fortress of the Legion|Sunhome]] are all just [[Wastes]] as far as the computer is concerned. Also no difference between [[Bojuka Bog]], [[Tolaria West]], and [[Valakut, the Molten Pinnacle|Valakut]].


## Implementation

This app is written in Python using the [Django][django] framework.
There's also a bit of HTML, SCSS, and JS to make it look presentable.
Content is rendered on the server side then swapped in using [htmx][htmx]. 
You can peruse the source code yourself [on GitHub][github]. 

Dependencies are managed using Docker.
This is a matter of personal preference.
It also works fine with `pipenv`, `virtualenv`, or just installing from `requirements.txt` and running locally.


TODO: AWS, GitHub actions

[mtggoldfish]: https://www.mtggoldfish.com/archetype/amulet-titan
[django]: https://www.djangoproject.com/
[github]: https://github.com/charles-uno/django-amulet
[blog]: https://charles.uno/amulet-simulation
[htmx]: https://htpx.org
