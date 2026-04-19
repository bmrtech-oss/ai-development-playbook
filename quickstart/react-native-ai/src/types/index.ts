export interface AiRequest {
  prompt: string;
  maxTokens: number;
}

export interface AiResponse {
  generatedText: string;
  tokensUsed: number;
  confidence: number;
}
