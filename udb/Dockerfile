FROM eclipse-temurin:11

WORKDIR /app

RUN apt-get update
RUN apt-get install -y unzip mysql-client libtcnative-1

COPY ./* ./

ADD downloads downloads
ADD database database
ADD setup setup

RUN sh ./setup/install_domibus.sh
RUN sh ./setup/install_domibus_sample.sh

ENTRYPOINT [ "sh", "./entrypoint.sh" ]