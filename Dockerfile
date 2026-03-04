FROM eclipse-temurin:17-jdk-jammy

WORKDIR /app

# jar 복사
COPY backend/build/libs/*.jar app.jar

# 포트
EXPOSE 8080

# 실행
ENTRYPOINT ["java","-jar","app.jar"]