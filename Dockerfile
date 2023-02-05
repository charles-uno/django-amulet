FROM python:3.10-slim
WORKDIR /workdir
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY app ./app
# easier to run commands from within the app directory
WORKDIR /workdir/app
RUN python3 manage.py sass-compiler
# Unit tests only take a sec. Might as well run them
RUN pytest backend/amulet_model/tests
EXPOSE 8000
CMD ["gunicorn", "amulet_flashcards.wsgi", "-b", "0.0.0.0:8000"]
