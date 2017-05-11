FROM python:alpine

# TODO: use the requirements.txt
RUN pip3 install redis
RUN pip3 install pyyaml

WORKDIR src

COPY api-server /src

RUN /usr/bin/crontab /src/crontab.txt
CMD sh -c "/usr/sbin/crond -f -l 8"
