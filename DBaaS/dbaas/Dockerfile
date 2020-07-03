FROM tiangolo/uwsgi-nginx-flask:python3.7
ENV UWSGI_INI /app/uwsgi.ini
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
COPY ./app /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt