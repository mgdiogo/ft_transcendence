FROM python

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./user_service/app /app/
COPY ../shared_models/models.py /app/user_api/models.py

WORKDIR /app

COPY ./user_service/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000
