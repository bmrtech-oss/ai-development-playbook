package com.example.ai.controller;

import com.example.ai.service.AiService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(AiController.class)
class AiControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private AiService aiService;

    @Test
    void generateText_ValidRequest_ReturnsResponse() throws Exception {
        // Given
        String requestJson = """
            {
                "prompt": "Test prompt",
                "maxTokens": 100
            }
            """;

        AiController.AiResponse mockResponse = new AiController.AiResponse(
            "Generated text", 25, 0.85
        );

        when(aiService.generateText(any())).thenReturn(mockResponse);

        // When & Then
        mockMvc.perform(post("/api/ai/generate")
                .contentType(MediaType.APPLICATION_JSON)
                .content(requestJson))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.generatedText").value("Generated text"))
                .andExpect(jsonPath("$.tokensUsed").value(25))
                .andExpect(jsonPath("$.confidence").value(0.85));
    }

    @Test
    void generateText_InvalidRequest_ReturnsBadRequest() throws Exception {
        // Given
        String invalidRequestJson = """
            {
                "prompt": "",
                "maxTokens": -1
            }
            """;

        // When & Then
        mockMvc.perform(post("/api/ai/generate")
                .contentType(MediaType.APPLICATION_JSON)
                .content(invalidRequestJson))
                .andExpect(status().isBadRequest());
    }
}
