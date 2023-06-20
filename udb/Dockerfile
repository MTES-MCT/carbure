FROM eclipse-temurin:11

WORKDIR /app

RUN wget https://ec.europa.eu/digital-building-blocks/artifact/content/repositories/public/eu/domibus/domibus-distribution/5.0.4/domibus-distribution-5.0.4-tomcat-full.zip
RUN wget https://ec.europa.eu/digital-building-blocks/artifact/content/repositories/public/eu/domibus/domibus-distribution/5.0.4/domibus-distribution-5.0.4-sample-configuration-and-testing.zip
RUN wget https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-j-8.0.32.zip

RUN apt-get update
RUN apt-get install -y unzip mysql-client

RUN unzip -d . domibus-distribution-5.0.4-tomcat-full.zip
RUN unzip -d ./domibus domibus-distribution-5.0.4-sample-configuration-and-testing.zip
RUN unzip -d /tmp mysql-connector-j-8.0.32.zip

RUN mv /tmp/mysql-connector-j-8.0.32/mysql-connector-j-8.0.32.jar ./domibus/lib

RUN rm *.zip

RUN chmod +x ./domibus/bin/*.sh

ENTRYPOINT [ "./domibus/bin/catalina.sh",  "run" ]