import { generateText } from '../src/services/openai';

describe('OpenAI Service', () => {
  it('generateText returns expected structure', async () => {
    const request = {
      prompt: 'Test prompt',
      maxTokens: 100,
    };

    const result = await generateText(request);

    expect(result).toHaveProperty('generatedText');
    expect(result).toHaveProperty('tokensUsed');
    expect(result).toHaveProperty('confidence');
    expect(typeof result.generatedText).toBe('string');
    expect(typeof result.tokensUsed).toBe('number');
    expect(typeof result.confidence).toBe('number');
  });

  it('generateText handles empty prompt', async () => {
    const request = {
      prompt: '',
      maxTokens: 100,
    };

    await expect(generateText(request)).rejects.toThrow();
  });
});
