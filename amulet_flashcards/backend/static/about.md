## About the Model

The MTG deck [Amulet Titan][mtggoldfish] is known for its complex play patterns. 
This app presents users with sample opening hands, then shuffles the deck and solves for a sequence of plays to cast the titular [[Primeval Titan|Titan]] as quickly as possible. 
Think of it like mulligan flashcards: decide for yourself whether you would keep the hand, then play it out a few times to see what the numbers say!

[mtggoldfish]: https://www.mtggoldfish.com/archetype/amulet-titan

Sequencing is determined via exhaustive search.
Whenever the computer is faced with a choice, it tries both options and keeps whichever works out best.
For example, an experienced player can generally eyeball whether to choose land or nonland for [[Abundant Harvest]], but spelling out the logic explicitly for the computer is tedious and fragile.
Instead of worrying about strategy and synergy, the computer splits the game into two copies.
The first chooses land, the second chooses nonland, and they proceed independently from there.
If either copy ends up casting turn-three [[Primeval Titan]] down the line, it's pretty safe to say that a human player could have done so as well.

Exhaustive search is straightforward and flexible, but also computationally demanding.
Several approximations are made in the interest of performance.
Oddball singletons like [[Boros Garrison]], [[Cavern of Souls]], and [[Vesuva]] are excluded.
Only green mana is tracked, so there's no transmuting with [[Tolaria West]].
There's no need to worry about the non-mana abilities on [[Slayers' Stronghold]] or [[Sunhome, Fortress of the Legion|Sunhome]], so those are represented by additional copies of [[Radiant Fountain]].
Similarly, [[Bojuka Bog]] is used as a stand-in for any non-green land that enters the battlefield tapped, such as [[Valakut, the Molten Pinnacle|Valakut]].
These approximations can make opening hands look a bit odd, but the resulting numbers turn out to be nearly identical.

That said, please don't expect the computer to teach you good sequencing!
If it's possible to cast [[Primeval Titan]] on turn three, this model is guaranteed to find a way to do so.
But there are often several different ways to get there.
There's no guarantee the computer will pick the best one.
Several corrections are included to suppress non-human play patterns, but from time to time it'll still choose a "solution" that's needlessly bizarre or reckless.
Consider it a starting point, not an authority.

## The Deck List

Below is the list used by this app. Don't worry too much about a difference here or there. 
Considering similar cards together helps the model run faster. Numbers look pretty much the same if (for example) we swap out an [[Explore]] for an [[Azusa, Lost but Seeking|Azusa]].

TODO: import decklist?

## Implementation

- Python/Django
- A sprinkling of HTML, CSS and JS to make it presentable
- AJAX requests to the backend use HTMX
- Docker
- TODO: AWS, GitHub Actions

You can check out the source [on GitHub][source]

The model is a simplified version of the one from my previous work [here][blog]

[source]: https://github.com/charles-uno/django-amulet
[blog]: https://charles.uno/amulet-simulation

## Fine Print

Privacy policy: I don't store user data. But I do use some third-party stuff like htmx and Google Fonts

This page &copy; Charles Fyfe 2023

Unofficial [fan content][fan_content_policy]. Not affiliated or endorsed

[fan_content_policy]: https://company.wizards.com/en/legal/fancontentpolicy

