# Java Spring AI Starter Kit

This starter kit demonstrates a Java Spring Boot application with AI integration using Spring AI and OpenAI.

## Features
- REST API with AI-powered text generation
- Schema validation with Bean Validation
- Unit and integration tests
- Docker containerization
- CI/CD with GitHub Actions

## Prerequisites
- Java 17+
- Maven 3.6+
- Docker
- OpenAI API key

## Quick Start

1. Clone and navigate to this directory
2. Set environment variable: `export OPENAI_API_KEY=your_key_here`
3. Run: `mvn spring-boot:run`
4. Test: `curl -X POST http://localhost:8080/api/ai/generate -H "Content-Type: application/json" -d '{"prompt":"Hello AI","maxTokens":50}'`

## Project Structure
```
src/
├── main/java/com/example/ai/
│   ├── controller/AiController.java
│   ├── service/AiService.java
│   ├── config/AiConfig.java
│   └── AiApplication.java
└── test/java/com/example/ai/
    ├── controller/AiControllerTest.java
    └── service/AiServiceTest.java
```

## Deployment

### Docker
```bash
docker build -t java-ai-app .
docker run -p 8080:8080 -e OPENAI_API_KEY=your_key java-ai-app
```

### Kubernetes
```bash
kubectl apply -f k8s/deployment.yaml
```

## Testing
```bash
mvn test                    # Unit tests
mvn integration-test        # Integration tests
mvn verify                  # All tests + quality checks
```
