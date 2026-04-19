const OpenAI = require('openai');

let openai = null;
if (process.env.OPENAI_API_KEY) {
  openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
  });
}

const generateText = async (request) => {
  // In a real implementation, you'd call OpenAI here
  // For demo purposes, returning mock response
  const mockResponse = `Generated response for: ${request.prompt}`;
  const tokensUsed = Math.ceil(request.prompt.length / 4); // Rough estimate
  const confidence = 0.85;

  return {
    generatedText: mockResponse,
    tokensUsed,
    confidence
  };
};

module.exports = {
  generateText
};
