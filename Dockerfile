FROM python:3.10-slim
WORKDIR /workdir
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY amulet_flashcards ./amulet_flashcards
RUN python3 amulet_flashcards/manage.py sass-compiler
EXPOSE 8000
CMD ["python3", "amulet_flashcards/manage.py", "runserver", "0.0.0.0:8000"]
