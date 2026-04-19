import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { generateText as callOpenAI } from '../services/openai';

export interface AiRequest {
  prompt: string;
  maxTokens: number;
}

export interface AiResponse {
  generatedText: string;
  tokensUsed: number;
  confidence: number;
}

interface AiState {
  loading: boolean;
  result: AiResponse | null;
  error: string | null;
}

const initialState: AiState = {
  loading: false,
  result: null,
  error: null,
};

export const generateText = createAsyncThunk(
  'ai/generateText',
  async (request: AiRequest) => {
    const response = await callOpenAI(request);
    return response;
  }
);

const aiSlice = createSlice({
  name: 'ai',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(generateText.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(generateText.fulfilled, (state, action: PayloadAction<AiResponse>) => {
        state.loading = false;
        state.result = action.payload;
      })
      .addCase(generateText.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'An error occurred';
      });
  },
});

export const selectAiState = (state: { ai: AiState }) => state.ai;
export default aiSlice.reducer;
