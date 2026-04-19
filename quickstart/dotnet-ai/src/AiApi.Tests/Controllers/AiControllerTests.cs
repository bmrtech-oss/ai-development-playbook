using AiApi.Controllers;
using AiApi.Services;
using Microsoft.AspNetCore.Mvc;
using Moq;

namespace AiApi.Tests.Controllers;

public class AiControllerTests
{
    private readonly Mock<AiService> _aiServiceMock;
    private readonly AiController _controller;

    public AiControllerTests()
    {
        _aiServiceMock = new Mock<AiService>(null!);
        _controller = new AiController(_aiServiceMock.Object);
    }

    [Fact]
    public async Task Generate_ValidRequest_ReturnsOkResult()
    {
        // Arrange
        var request = new AiRequest("Test prompt", 100);
        var expectedResponse = new AiResponse("Generated text", 25, 0.85);
        _aiServiceMock.Setup(x => x.GenerateTextAsync(request))
            .ReturnsAsync(expectedResponse);

        // Act
        var result = await _controller.Generate(request);

        // Assert
        var okResult = Assert.IsType<OkObjectResult>(result);
        var response = Assert.IsType<AiResponse>(okResult.Value);
        Assert.Equal(expectedResponse.GeneratedText, response.GeneratedText);
    }

    [Fact]
    public async Task Generate_InvalidRequest_ReturnsBadRequest()
    {
        // Arrange
        var request = new AiRequest("", 0); // Invalid
        _controller.ModelState.AddModelError("Prompt", "Required");

        // Act
        var result = await _controller.Generate(request);

        // Assert
        Assert.IsType<BadRequestObjectResult>(result);
    }
}
