const Joi = require('joi');

const aiRequestSchema = Joi.object({
  prompt: Joi.string().min(1).max(1000).required()
    .messages({
      'string.empty': 'Prompt cannot be empty',
      'string.max': 'Prompt cannot exceed 1000 characters'
    }),
  maxTokens: Joi.number().integer().min(1).max(1000).default(100)
    .messages({
      'number.min': 'Max tokens must be at least 1',
      'number.max': 'Max tokens cannot exceed 1000'
    })
});

module.exports = {
  aiRequestSchema
};
