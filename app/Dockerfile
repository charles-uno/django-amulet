FROM python:3.10-slim
# Note: call docker build from the root of the repo (one level up)
COPY app /app
WORKDIR /app
RUN pip3 install -r requirements.txt
RUN python3 manage.py sass-compiler
# Unit tests only take a sec. Might as well run them
RUN pytest backend/amulet_model/tests
EXPOSE 8000
CMD ["gunicorn", "amulet_flashcards.wsgi", "-b", "0.0.0.0:8000"]
