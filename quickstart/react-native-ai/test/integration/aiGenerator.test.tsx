import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import AiGenerator from '../src/components/AiGenerator';
import { Provider } from 'react-redux';
import { store } from '../src/stores/store';

const renderWithProvider = (component: React.ReactElement) => {
  return render(
    <Provider store={store}>
      {component}
    </Provider>
  );
};

describe('AiGenerator Component', () => {
  it('renders correctly', () => {
    const { getByText } = renderWithProvider(<AiGenerator />);
    expect(getByText('AI Text Generator')).toBeTruthy();
  });

  it('shows validation error for empty prompt', async () => {
    const { getByText, getByPlaceholderText } = renderWithProvider(<AiGenerator />);

    const submitButton = getByText('Generate Text');
    fireEvent.press(submitButton);

    await waitFor(() => {
      expect(getByText('Prompt is required')).toBeTruthy();
    });
  });
});
