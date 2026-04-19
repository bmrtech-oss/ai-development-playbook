using Microsoft.Extensions.AI;

namespace AiApi.Services;

public class AiService
{
    private readonly IChatClient _chatClient;

    public AiService(IChatClient chatClient)
    {
        _chatClient = chatClient;
    }

    public async Task<AiResponse> GenerateTextAsync(AiRequest request)
    {
        // In a real implementation, you'd call the AI model here
        // For demo purposes, returning mock response
        var mockResponse = $"Generated response for: {request.Prompt}";
        var tokensUsed = request.Prompt.Length / 4; // Rough estimate
        var confidence = 0.85;

        return new AiResponse(mockResponse, tokensUsed, confidence);
    }
}
