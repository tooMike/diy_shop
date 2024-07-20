FROM debian:buster

RUN apt-get update && apt-get install -y postfix

# Настройка Postfix для работы в режиме "интернет сайта"
RUN echo "postfix postfix/mailname string your.domain.com" | debconf-set-selections
RUN echo "postfix postfix/main_mailer_type string 'Internet Site'" | debconf-set-selections
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y postfix

# Конфигурация Postfix для принятия почты от всех IP
RUN sed -i 's/inet_interfaces = localhost/inet_interfaces = all/' /etc/postfix/main.cf
RUN sed -i 's/mynetworks = 127.0.0.0\/8/mynetworks = 0.0.0.0\/0/' /etc/postfix/main.cf

EXPOSE 25

CMD ["postfix", "start-fg"]
