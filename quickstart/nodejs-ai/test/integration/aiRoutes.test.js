const request = require('supertest');
const app = require('../../src/app');

describe('AI Routes', () => {
  test('POST /api/ai/generate returns 200 with valid request', async () => {
    const response = await request(app)
      .post('/api/ai/generate')
      .send({
        prompt: 'Test prompt',
        maxTokens: 100
      })
      .expect(200);

    expect(response.body).toHaveProperty('generatedText');
    expect(response.body).toHaveProperty('tokensUsed');
    expect(response.body).toHaveProperty('confidence');
  });

  test('POST /api/ai/generate returns 400 with invalid request', async () => {
    const response = await request(app)
      .post('/api/ai/generate')
      .send({
        prompt: '',
        maxTokens: -1
      })
      .expect(400);

    expect(response.body).toHaveProperty('error');
  });
});
