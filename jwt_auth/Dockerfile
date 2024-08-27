FROM python

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./jwt_auth/app /app/
COPY ../shared_models/models.py /app/jwt_api/models.py

WORKDIR /app

COPY ./jwt_auth/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8001
