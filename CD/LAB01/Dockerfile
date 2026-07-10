FROM openjdk:21
RUN mkdir /usr/executables
COPY ServiceREST.jar /usr/executables
RUN mkdir /usr/datafiles
WORKDIR /usr/datafiles
ENTRYPOINT ["java", "-jar", "/usr/executables/ServiceREST.jar"]