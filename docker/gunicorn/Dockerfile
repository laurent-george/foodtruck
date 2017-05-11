FROM python:alpine

# TODO: use the requirements.txt
RUN pip3 install gunicorn
RUN pip3 install hug -U
RUN pip3 install redis
RUN pip3 install requests
RUN pip3 install pyyaml


COPY api-server /src

EXPOSE 8000
WORKDIR src
CMD sh -c "python populate_db.py && gunicorn --reload --bind=0.0.0.0:8000 api:__hug_wsgi__"
#CMD hug -f api.py

