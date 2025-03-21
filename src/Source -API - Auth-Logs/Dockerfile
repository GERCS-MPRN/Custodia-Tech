FROM maven:3-eclipse-temurin-21-alpine AS MAVEN_BUILD

MAINTAINER Rivaldo Xavier da Silva
COPY pom.xml /build/
COPY src /build/src/
WORKDIR /build/

RUN mvn clean install && mvn package -f pom.xml
FROM eclipse-temurin:21
WORKDIR /app
COPY --from=MAVEN_BUILD /build/target/custodiatech-api-*.jar /app/custodiatech-api.jar

EXPOSE 80

ENTRYPOINT ["java", "-jar", "custodiatech-api.jar"]

