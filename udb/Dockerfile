FROM eclipse-temurin:11

WORKDIR /app

RUN apt-get update
RUN apt-get install -y unzip mysql-client

COPY ./* ./
RUN sh ./download_domibus.sh

ENTRYPOINT [ "sh", "./entrypoint_docker.sh" ]