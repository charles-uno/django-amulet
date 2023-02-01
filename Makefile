TAG = django-amulet-image
HOST_PORT = 8001

docker-build:
	docker build -f Dockerfile -t $(TAG) .

docker-run: 
	docker run -p $(HOST_PORT):8000 $(TAG)

docker-model:
	docker run $(TAG) python3 -m amulet_flashcards.backend.amulet_model

docker-test:
	docker run $(TAG) make -C amulet_flashcards