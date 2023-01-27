test:
	for DIR in $$(ls */Makefile | xargs dirname); do cd $$DIR && make test; cd ..; done

run:
	python3 manage.py runserver