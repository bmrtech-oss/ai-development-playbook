const aiService = require('../../src/services/aiService');

describe('AI Service', () => {
  test('generateText returns expected structure', async () => {
    const request = {
      prompt: 'Test prompt',
      maxTokens: 100
    };

    const result = await aiService.generateText(request);

    expect(result).toHaveProperty('generatedText');
    expect(result).toHaveProperty('tokensUsed');
    expect(result).toHaveProperty('confidence');
    expect(typeof result.generatedText).toBe('string');
    expect(typeof result.tokensUsed).toBe('number');
    expect(typeof result.confidence).toBe('number');
  });

  test('generateText handles empty prompt gracefully', async () => {
    const request = {
      prompt: '',
      maxTokens: 100
    };

    const result = await aiService.generateText(request);

    expect(result).toHaveProperty('generatedText');
    expect(result.generatedText).toContain('Generated response for:');
    expect(result).toHaveProperty('tokensUsed');
    expect(result).toHaveProperty('confidence');
  });
});
