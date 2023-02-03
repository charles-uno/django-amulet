FROM python:3.10-slim
RUN mkdir /workdir
COPY requirements.txt /workdir/
RUN pip3 install -r /workdir/requirements.txt
COPY amulet_flashcards /workdir/amulet_flashcards
WORKDIR /workdir/amulet_flashcards
RUN python3 manage.py sass-compiler
# Unit tests only take a sec. Might as well run them
RUN pytest backend/amulet_model/tests
EXPOSE 8000
CMD ["gunicorn", "amulet_flashcards.wsgi", "0.0.0.0:8000"]
