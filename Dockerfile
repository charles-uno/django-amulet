FROM python:3.10-slim
WORKDIR /workdir
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY amulet_flashcards ./amulet_flashcards
# Note: there's a --watch flag if we want to do this dynamically
RUN python3 amulet_flashcards/manage.py sass-compiler
# Unit tests only take a sec. Might as well run them
RUN pytest amulet_flashcards/backend/amulet_model/tests
EXPOSE 8000
CMD ["python3", "amulet_flashcards/manage.py", "runserver", "0.0.0.0:8000"]
