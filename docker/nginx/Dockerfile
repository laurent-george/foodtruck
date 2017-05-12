#FROM nginx:latest
#RUN rm /etc/nginx/conf.d/default.conf
#COPY nginx.conf /etc/nginx.conf
#ADD sites-enabled/ /etc/nginx/sites-enabled
FROM tutum/nginx
RUN rm /etc/nginx/sites-enabled/default
ADD sites-enabled/ /etc/nginx/sites-enabled


EXPOSE 80


