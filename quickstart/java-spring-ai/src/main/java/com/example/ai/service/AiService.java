package com.example.ai.service;

import com.example.ai.controller.AiController;
import org.springframework.ai.openai.OpenAiChatModel;
import org.springframework.ai.openai.api.OpenAiApi;
import org.springframework.stereotype.Service;

@Service
public class AiService {

    private final OpenAiChatModel chatModel;

    public AiService(OpenAiChatModel chatModel) {
        this.chatModel = chatModel;
    }

    public AiController.AiResponse generateText(AiController.AiRequest request) {
        // In a real implementation, you'd call the AI model here
        // For demo purposes, returning mock response
        String mockResponse = "Generated response for: " + request.prompt();
        int tokensUsed = request.prompt().length() / 4; // Rough estimate
        double confidence = 0.85;

        return new AiController.AiResponse(mockResponse, tokensUsed, confidence);
    }
}
