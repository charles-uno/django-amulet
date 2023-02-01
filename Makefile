TAG = django-amulet-image
HOST_PORT = 8001


# Build the Docker image that all subsequent recipes use. Only takes a minute
build:
	docker build -f Dockerfile -t $(TAG) .


# Launch the Django app
run: 
	docker run -p $(HOST_PORT):8000 $(TAG)


# Runs the model once as a sanity check (no Django) and prints to the shell
model:
	docker run $(TAG) python3 -m amulet_flashcards.backend.amulet_model


# Runs the unit tests
test:
	docker run $(TAG) pytest amulet_flashcards/backend/amulet_model/tests