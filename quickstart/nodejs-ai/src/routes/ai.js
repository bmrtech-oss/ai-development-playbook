const express = require('express');
const { aiRequestSchema } = require('../middleware/validation');
const aiService = require('../services/aiService');

const router = express.Router();

router.post('/generate', async (req, res) => {
  try {
    // Validate request
    const { error, value } = aiRequestSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ error: error.details[0].message });
    }

    // Generate response
    const response = await aiService.generateText(value);
    res.json(response);
  } catch (err) {
    console.error('Error generating AI response:', err);
    res.status(500).json({ error: 'Failed to generate AI response' });
  }
});

module.exports = router;
