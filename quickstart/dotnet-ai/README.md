# .NET AI Starter Kit

This starter kit demonstrates a .NET 8 application with AI integration using Microsoft.Extensions.AI and OpenAI.

## Features
- ASP.NET Core Web API with AI-powered text generation
- Data validation with DataAnnotations
- Unit and integration tests with xUnit
- Docker containerization
- CI/CD with GitHub Actions

## Prerequisites
- .NET 8 SDK
- Docker
- OpenAI API key

## Quick Start

1. Clone and navigate to this directory
2. Set environment variable: `export OPENAI_API_KEY=your_key_here`
3. Run: `dotnet run`
4. Test: `curl -X POST https://localhost:5001/api/ai/generate -H "Content-Type: application/json" -d '{"prompt":"Hello AI","maxTokens":50}'`

## Project Structure
```
src/
├── AiApi/
│   ├── Controllers/AiController.cs
│   ├── Services/AiService.cs
│   ├── Program.cs
│   └── appsettings.json
└── AiApi.Tests/
    ├── Controllers/AiControllerTests.cs
    └── Services/AiServiceTests.cs
```

## Deployment

### Docker
```bash
docker build -t dotnet-ai-app .
docker run -p 8080:8080 -e OPENAI_API_KEY=your_key dotnet-ai-app
```

### Azure
```bash
az webapp up --name dotnet-ai-app --resource-group myResourceGroup --runtime "DOTNETCORE:8.0"
```

## Testing
```bash
dotnet test                    # Run all tests
dotnet test --filter "Category=Unit"    # Unit tests only
dotnet test --filter "Category=Integration"  # Integration tests only
```
