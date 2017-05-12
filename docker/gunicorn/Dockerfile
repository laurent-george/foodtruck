FROM python:alpine
RUN apk add --update python-dev build-base
# TODO: use the requirements.txt
RUN pip3 install gunicorn
RUN pip3 install hug -U
RUN pip3 install redis
RUN pip3 install requests
RUN pip3 install pyyaml
RUN pip3 install gevent

#COPY api-server /src

EXPOSE 8000
WORKDIR src
# TODO: set number of worker based on amazon/digitalocean hw, TODO: check gevent..
CMD sh -c "python populate_db.py && gunicorn --workers 4 -k gevent --worker-connections 1000 --reload --bind=0.0.0.0:8000 api:__hug_wsgi__"
#CMD hug -f api.py

