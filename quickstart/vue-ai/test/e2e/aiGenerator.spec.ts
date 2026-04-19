import { test, expect } from '@playwright/test'

test.describe('AI Generator E2E', () => {
  test('should generate text with valid input', async ({ page }) => {
    await page.goto('http://localhost:5173')

    // Fill form
    await page.fill('textarea[id="prompt"]', 'Test prompt for AI generation')
    await page.fill('input[id="maxTokens"]', '100')

    // Submit form
    await page.click('button[type="submit"]')

    // Wait for result
    await page.waitForSelector('.result')

    // Check result
    const generatedText = await page.textContent('.result p')
    expect(generatedText).toContain('Generated response for:')
  })

  test('should show validation error for empty prompt', async ({ page }) => {
    await page.goto('http://localhost:5173')

    // Leave prompt empty and submit
    await page.click('button[type="submit"]')

    // Check for error message
    const errorMessage = await page.textContent('.error-message')
    expect(errorMessage).toContain('required')
  })
})
