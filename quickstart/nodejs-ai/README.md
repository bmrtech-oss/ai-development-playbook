# Node.js AI Starter Kit

This starter kit demonstrates a Node.js application with AI integration using OpenAI SDK and Express.js.

## Features
- Express.js REST API with AI-powered text generation
- Input validation with Joi
- Unit and integration tests with Jest
- Docker containerization
- CI/CD with GitHub Actions

## Prerequisites
- Node.js 18+
- npm or yarn
- Docker
- OpenAI API key

## Quick Start

1. Clone and navigate to this directory
2. Install dependencies: `npm install`
3. Set environment variable: `export OPENAI_API_KEY=your_key_here`
4. Run: `npm start`
5. Test: `curl -X POST http://localhost:3000/api/ai/generate -H "Content-Type: application/json" -d '{"prompt":"Hello AI","maxTokens":50}'`

## Project Structure
```
src/
├── controllers/
│   └── aiController.js
├── services/
│   └── aiService.js
├── middleware/
│   └── validation.js
├── routes/
│   └── ai.js
├── app.js
└── config/
    └── openai.js
test/
├── unit/
│   └── aiService.test.js
└── integration/
    └── aiRoutes.test.js
```

## Deployment

### Docker
```bash
docker build -t nodejs-ai-app .
docker run -p 3000:3000 -e OPENAI_API_KEY=your_key nodejs-ai-app
```

### Railway or Render
```bash
npm run build
# Deploy the built app
```

## Testing
```bash
npm test                    # Run all tests
npm run test:unit           # Unit tests only
npm run test:integration    # Integration tests only
npm run test:coverage       # Tests with coverage report
```
