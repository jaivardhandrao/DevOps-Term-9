FROM eclipse-temurin:21-jdk-alpine AS builder

WORKDIR /src
COPY src/Main.java .
RUN javac Main.java

FROM eclipse-temurin:21-jre-alpine

RUN addgroup -S app && adduser -S app -G app
WORKDIR /app
COPY --from=builder --chown=app:app /src/Main.class .

USER app
EXPOSE 8080
CMD ["java", "Main"]
