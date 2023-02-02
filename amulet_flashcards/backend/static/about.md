## About the Model

The MTG deck [Amulet Titan][mtggoldfish] is known for its complex play patterns. 
This app presents users with sample opening hands, then shuffles the deck and solves for a sequence of plays to cast the titular [[Primeval Titan|Titan]] as quickly as possible. 
Think of it like flashcards: decide for yourself whether you would keep the hand, then play it out a few times to see what the numbers say!

[mtggoldfish]: https://www.mtggoldfish.com/archetype/amulet-titan

Sequencing is determined via exhaustive search.
Whenever the computer is faced with a choice, it tries both options and keeps whichever works out best.
For example, an experienced player can generally eyeball whether to choose land or nonland for [[Abundant Harvest]], but spelling out the logic explicitly for the computer is tedious and fragile.
Instead of worrying about strategy and synergy, the computer splits the game into two copies.
The first chooses land, the second chooses nonland, and they proceed independently from there.
If either copy ends up casting turn-three [[Primeval Titan]] down the line, it's pretty safe to say that a human player could have done so as well.

That said, please don't expect this model to teach you good sequencing!
If it's possible to cast [[Primeval Titan]] (or [[Cultivator Colossus]]) by turn three, it's guaranteed to find a way to do so.
But in a real game, you also need to worry about developing your mana, playing around interaction, and paying for your [[Summoner's Pact|Pact]] on turn four.
Consider this a starting point, not an authority.

## The Deck List

The model uses the list below. 
You may notice that [[Cavern of Souls]] and [[Vesuva]] have been swapped out due to complexity.
Don't worry too much about it. 
The numbers and play patterns are still pretty much the same.

$DECKLIST


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

