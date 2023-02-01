TAG = django-image
HOST_PORT = 8001


docker-build:
	docker build -f Dockerfile -t $(TAG) .

docker-run:
	docker run -p $(HOST_PORT):8000 $(TAG)