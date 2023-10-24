FROM eclipse-temurin:11

WORKDIR /app

RUN apt-get update
RUN apt-get install -y unzip mysql-client libtcnative-1

COPY ./* ./
ADD downloads downloads
RUN sh ./download_domibus.sh
RUN mv setenv.sh ./domibus/bin/

ENTRYPOINT [ "sh", "./entrypoint_docker.sh" ]