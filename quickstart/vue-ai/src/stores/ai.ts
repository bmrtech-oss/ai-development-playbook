import { defineStore } from 'pinia'
import { generateText } from '../services/openai'

export interface AiRequest {
  prompt: string
  maxTokens: number
}

export interface AiResponse {
  generatedText: string
  tokensUsed: number
  confidence: number
}

export const useAiStore = defineStore('ai', {
  state: () => ({
    loading: false,
    result: null as AiResponse | null,
    error: null as string | null
  }),

  actions: {
    async generateText(request: AiRequest) {
      this.loading = true
      this.error = null
      this.result = null

      try {
        const response = await generateText(request)
        this.result = response
      } catch (err) {
        this.error = err instanceof Error ? err.message : 'An error occurred'
      } finally {
        this.loading = false
      }
    }
  }
})
