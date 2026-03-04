FROM python:3.9-slim

WORKDIR /app

COPY geometric_lib /geometric_lib

COPY app.py .

RUN chmod +x app.py

CMD [ "python", "app.py" ]