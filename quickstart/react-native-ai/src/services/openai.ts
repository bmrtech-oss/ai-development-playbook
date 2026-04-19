import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.EXPO_PUBLIC_OPENAI_API_KEY,
  dangerouslyAllowBrowser: true,
});

export interface AiRequest {
  prompt: string;
  maxTokens: number;
}

export interface AiResponse {
  generatedText: string;
  tokensUsed: number;
  confidence: number;
}

export const generateText = async (request: AiRequest): Promise<AiResponse> => {
  // In a real implementation, you'd call OpenAI here
  // For demo purposes, returning mock response
  const mockResponse = `Generated response for: ${request.prompt}`;
  const tokensUsed = Math.ceil(request.prompt.length / 4);
  const confidence = 0.85;

  return {
    generatedText: mockResponse,
    tokensUsed,
    confidence,
  };
};
