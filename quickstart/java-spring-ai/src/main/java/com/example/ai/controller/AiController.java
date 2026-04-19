package com.example.ai.controller;

import com.example.ai.service.AiService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Positive;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/ai")
public class AiController {

    private final AiService aiService;

    public AiController(AiService aiService) {
        this.aiService = aiService;
    }

    @PostMapping("/generate")
    public ResponseEntity<AiResponse> generate(@Valid @RequestBody AiRequest request) {
        AiResponse response = aiService.generateText(request);
        return ResponseEntity.ok(response);
    }

    public record AiRequest(
        @NotBlank(message = "Prompt cannot be blank")
        String prompt,
        @Positive(message = "Max tokens must be positive")
        int maxTokens
    ) {}

    public record AiResponse(
        String generatedText,
        int tokensUsed,
        double confidence
    ) {}
}
