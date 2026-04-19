# React Native AI Starter Kit

This starter kit demonstrates a React Native mobile application with AI integration using OpenAI SDK and Expo.

## Features
- React Native with Expo
- AI-powered text generation interface
- Form validation with Formik and Yup
- Unit and integration tests with Jest
- CI/CD with GitHub Actions
- iOS and Android support

## Prerequisites
- Node.js 18+
- npm or yarn
- Expo CLI
- OpenAI API key
- iOS Simulator or Android Emulator

## Quick Start

1. Clone and navigate to this directory
2. Install dependencies: `npm install`
3. Set environment variable: `export EXPO_PUBLIC_OPENAI_API_KEY=your_key_here`
4. Start Expo: `npx expo start`
5. Run on simulator/emulator

## Project Structure
```
src/
├── components/
│   ├── AiGenerator.tsx
│   └── App.tsx
├── services/
│   └── openai.ts
├── types/
│   └── index.ts
├── utils/
│   └── validation.ts
└── stores/
    └── aiSlice.ts
test/
├── unit/
│   └── openaiService.test.ts
└── integration/
    └── aiGenerator.test.tsx
```

## Deployment

### Expo Application Services
```bash
npx expo build:ios
npx expo build:android
```

### App Store / Play Store
```bash
npx expo build:ios --type archive
npx expo build:android --type app-bundle
```

## Testing
```bash
npm test                    # Run all tests
npm run test:unit           # Unit tests only
npm run test:integration    # Integration tests only
npm run test:coverage       # Tests with coverage report
```
