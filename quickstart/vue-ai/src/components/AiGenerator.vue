<template>
  <div class="ai-generator">
    <h1>AI Text Generator</h1>

    <form @submit.prevent="generateText" class="generator-form">
      <div class="form-group">
        <label for="prompt">Prompt:</label>
        <textarea
          id="prompt"
          v-model="form.prompt"
          :class="{ error: v$.prompt.$error }"
          placeholder="Enter your prompt here..."
        ></textarea>
        <span v-if="v$.prompt.$error" class="error-message">
          {{ v$.prompt.$errors[0].$message }}
        </span>
      </div>

      <div class="form-group">
        <label for="maxTokens">Max Tokens:</label>
        <input
          id="maxTokens"
          type="number"
          v-model.number="form.maxTokens"
          :class="{ error: v$.maxTokens.$error }"
          min="1"
          max="1000"
        />
        <span v-if="v$.maxTokens.$error" class="error-message">
          {{ v$.maxTokens.$errors[0].$message }}
        </span>
      </div>

      <button type="submit" :disabled="loading || v$.$invalid">
        {{ loading ? 'Generating...' : 'Generate Text' }}
      </button>
    </form>

    <div v-if="result" class="result">
      <h3>Generated Text:</h3>
      <p>{{ result.generatedText }}</p>
      <div class="metadata">
        <span>Tokens Used: {{ result.tokensUsed }}</span>
        <span>Confidence: {{ result.confidence }}</span>
      </div>
    </div>

    <div v-if="error" class="error">
      Error: {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import { required, minLength, maxLength, minValue, maxValue } from '@vuelidate/validators'
import { useAiStore } from '../stores/ai'

const aiStore = useAiStore()

const form = reactive({
  prompt: '',
  maxTokens: 100
})

const rules = computed(() => ({
  prompt: {
    required,
    minLength: minLength(1),
    maxLength: maxLength(1000)
  },
  maxTokens: {
    minValue: minValue(1),
    maxValue: maxValue(1000)
  }
}))

const v$ = useVuelidate(rules, form)

const loading = computed(() => aiStore.loading)
const result = computed(() => aiStore.result)
const error = computed(() => aiStore.error)

const generateText = async () => {
  const isValid = await v$.value.$validate()
  if (!isValid) return

  await aiStore.generateText(form)
}
</script>

<style scoped>
.ai-generator {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.generator-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 30px;
}

.form-group {
  display: flex;
  flex-direction: column;
  text-align: left;
}

label {
  margin-bottom: 5px;
  font-weight: bold;
}

textarea, input {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

textarea {
  min-height: 100px;
  resize: vertical;
}

.error {
  border-color: #e74c3c;
}

.error-message {
  color: #e74c3c;
  font-size: 14px;
  margin-top: 5px;
}

button {
  padding: 12px 24px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover:not(:disabled) {
  background-color: #2980b9;
}

button:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.result {
  text-align: left;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 4px;
  margin-top: 20px;
}

.metadata {
  margin-top: 10px;
  font-size: 14px;
  color: #666;
}

.metadata span {
  margin-right: 20px;
}
</style>
