#file from https://github.com/timothycrosley/hug/blob/develop/docker/workspace/Dockerfile
FROM python:alpine
MAINTAINER Housni Yakoob <housni.yakoob@gmail.com>

RUN apk update && apk upgrade
RUN apk add bash \
    && sed -i -e "s/bin\/ash/bin\/bash/" /etc/passwd

CMD ["true"]