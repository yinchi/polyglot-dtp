FROM debian:trixie-slim
RUN apt-get update && apt-get install -y \
    phppgadmin \
    apache2 \
    libapache2-mod-php

EXPOSE 80
ENTRYPOINT ["apache2ctl", "-D", "FOREGROUND"]
