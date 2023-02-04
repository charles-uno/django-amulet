TAG = django-amulet-image
# TODO: put nginx on port 80
HOST_PORT = 8001


# Build the Docker image that all subsequent recipes use. Only takes a minute
build:
	docker build -f Dockerfile -t $(TAG) .


# Interactive session in the image to poke around
debug: build
	docker run -p $(HOST_PORT):8000 -it $(TAG) /bin/sh


# Launch the Django app
run:  build
	docker run -p $(HOST_PORT):8000 $(TAG)


# Runs the model once as a sanity check (no Django) and prints to the shell
model: build
	docker run $(TAG) python3 -m amulet_flashcards.backend.amulet_model


# Runs the unit tests
test: build
	docker run $(TAG) pytest amulet_flashcards/backend/amulet_model/tests