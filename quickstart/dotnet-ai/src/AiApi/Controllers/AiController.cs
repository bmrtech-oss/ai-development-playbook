using Microsoft.Extensions.AI;

namespace AiApi.Controllers;

[ApiController]
[Route("api/[controller]")]
public class AiController : ControllerBase
{
    private readonly AiService _aiService;

    public AiController(AiService aiService)
    {
        _aiService = aiService;
    }

    [HttpPost("generate")]
    public async Task<IActionResult> Generate([FromBody] AiRequest request)
    {
        if (!ModelState.IsValid)
        {
            return BadRequest(ModelState);
        }

        var response = await _aiService.GenerateTextAsync(request);
        return Ok(response);
    }
}

public record AiRequest(
    [Required] [StringLength(1000, MinimumLength = 1)] string Prompt,
    [Range(1, 1000)] int MaxTokens = 100
);

public record AiResponse(
    string GeneratedText,
    int TokensUsed,
    double Confidence
);
