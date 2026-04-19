# Vue.js AI Starter Kit

This starter kit demonstrates a Vue.js application with AI integration using OpenAI SDK and Pinia for state management.

## Features
- Vue 3 Composition API with TypeScript
- AI-powered text generation interface
- Form validation with Vuelidate
- Unit and E2E tests with Vitest and Playwright
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
3. Set environment variable: `export VITE_OPENAI_API_KEY=your_key_here`
4. Run: `npm run dev`
5. Open http://localhost:5173

## Project Structure
```
src/
├── components/
│   ├── AiGenerator.vue
│   └── App.vue
├── stores/
│   └── ai.ts
├── services/
│   └── openai.ts
├── types/
│   └── index.ts
├── utils/
│   └── validation.ts
└── main.ts
test/
├── unit/
│   └── aiService.test.ts
└── e2e/
    └── aiGenerator.spec.ts
```

## Deployment

### Docker
```bash
docker build -t vue-ai-app .
docker run -p 80:80 vue-ai-app
```

### Vercel
```bash
npm run build
# Deploy to Vercel
```

## Testing
```bash
npm run test:unit         # Unit tests with Vitest
npm run test:e2e          # E2E tests with Playwright
npm run test:coverage     # Tests with coverage report
```
