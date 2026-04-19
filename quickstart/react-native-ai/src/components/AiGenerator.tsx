import React from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { Formik } from 'formik';
import * as Yup from 'yup';
import { useDispatch, useSelector } from 'react-redux';
import { generateText, selectAiState } from '../stores/aiSlice';

const validationSchema = Yup.object().shape({
  prompt: Yup.string()
    .required('Prompt is required')
    .min(1, 'Prompt cannot be empty')
    .max(1000, 'Prompt cannot exceed 1000 characters'),
  maxTokens: Yup.number()
    .required('Max tokens is required')
    .min(1, 'Max tokens must be at least 1')
    .max(1000, 'Max tokens cannot exceed 1000'),
});

const AiGenerator: React.FC = () => {
  const dispatch = useDispatch();
  const { loading, result, error } = useSelector(selectAiState);

  const handleSubmit = (values: { prompt: string; maxTokens: number }) => {
    dispatch(generateText(values) as any);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>AI Text Generator</Text>

      <Formik
        initialValues={{ prompt: '', maxTokens: 100 }}
        validationSchema={validationSchema}
        onSubmit={handleSubmit}
      >
        {({ handleChange, handleBlur, handleSubmit, values, errors, touched, isValid }) => (
          <View style={styles.form}>
            <View style={styles.inputGroup}>
              <Text style={styles.label}>Prompt:</Text>
              <TextInput
                style={[styles.textInput, touched.prompt && errors.prompt && styles.errorInput]}
                multiline
                numberOfLines={4}
                onChangeText={handleChange('prompt')}
                onBlur={handleBlur('prompt')}
                value={values.prompt}
                placeholder="Enter your prompt here..."
              />
              {touched.prompt && errors.prompt && (
                <Text style={styles.errorText}>{errors.prompt}</Text>
              )}
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.label}>Max Tokens:</Text>
              <TextInput
                style={[styles.numberInput, touched.maxTokens && errors.maxTokens && styles.errorInput]}
                keyboardType="numeric"
                onChangeText={handleChange('maxTokens')}
                onBlur={handleBlur('maxTokens')}
                value={values.maxTokens.toString()}
              />
              {touched.maxTokens && errors.maxTokens && (
                <Text style={styles.errorText}>{errors.maxTokens}</Text>
              )}
            </View>

            <TouchableOpacity
              style={[styles.button, (!isValid || loading) && styles.disabledButton]}
              onPress={() => handleSubmit()}
              disabled={!isValid || loading}
            >
              <Text style={styles.buttonText}>
                {loading ? 'Generating...' : 'Generate Text'}
              </Text>
            </TouchableOpacity>
          </View>
        )}
      </Formik>

      {result && (
        <View style={styles.result}>
          <Text style={styles.resultTitle}>Generated Text:</Text>
          <Text style={styles.resultText}>{result.generatedText}</Text>
          <View style={styles.metadata}>
            <Text>Tokens Used: {result.tokensUsed}</Text>
            <Text>Confidence: {result.confidence}</Text>
          </View>
        </View>
      )}

      {error && (
        <View style={styles.error}>
          <Text style={styles.errorText}>Error: {error}</Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    width: '100%',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 30,
  },
  form: {
    width: '100%',
  },
  inputGroup: {
    marginBottom: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    minHeight: 100,
    textAlignVertical: 'top',
  },
  numberInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  errorInput: {
    borderColor: '#e74c3c',
  },
  errorText: {
    color: '#e74c3c',
    fontSize: 14,
    marginTop: 5,
  },
  button: {
    backgroundColor: '#3498db',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  disabledButton: {
    backgroundColor: '#bdc3c7',
  },
  buttonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
  result: {
    marginTop: 30,
    padding: 20,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  resultText: {
    fontSize: 16,
    marginBottom: 10,
  },
  metadata: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
});

export default AiGenerator;
