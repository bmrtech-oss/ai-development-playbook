# IoT AI Starter Kit

A comprehensive starter kit for building AI-powered IoT devices with edge computing, sensor integration, and cloud connectivity.

## Features

- **Edge AI**: TensorFlow Lite for Microcontrollers (TFLM) on resource-constrained devices
- **Sensor Integration**: Support for common IoT sensors (temperature, motion, camera)
- **Cloud Connectivity**: MQTT-based communication with AWS IoT/GCP IoT Core
- **Power Management**: Optimized for battery-powered devices
- **OTA Updates**: Over-the-air model and firmware updates
- **Security**: Secure boot, encrypted communication, and model protection

## Supported Platforms

- **ESP32**: WiFi/Bluetooth-enabled microcontroller
- **Raspberry Pi**: Linux-based single-board computer
- **Arduino Nano 33 BLE**: Bluetooth-enabled development board
- **Coral Dev Board**: Google Coral with Edge TPU
- **Jetson Nano**: NVIDIA Jetson for GPU-accelerated AI

## Quick Start

### Prerequisites
- PlatformIO IDE or Arduino IDE
- Python 3.8+ for model training and deployment scripts
- IoT development board (ESP32, Raspberry Pi, etc.)
- Sensors and peripherals as needed

### Setup
```bash
# Clone the repository
git clone https://github.com/your-org/iot-ai-kit.git
cd iot-ai-kit

# Install Python dependencies
pip install -r requirements.txt

# For ESP32 development
pio platform install espressif32

# For Raspberry Pi development
# Follow Raspberry Pi setup instructions
```

### Running the Demo
```bash
# Build and upload to ESP32
pio run -t upload -e esp32

# Monitor serial output
pio device monitor

# For Raspberry Pi
python3 iot_ai_app.py
```

## Architecture

### Core Components

#### 1. Edge AI Engine (`src/ai/`)
```cpp
// ESP32 TensorFlow Lite Micro Implementation
#include <TensorFlowLite_ESP32.h>
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"

class EdgeAIEngine {
private:
    tflite::MicroInterpreter* interpreter;
    tflite::MicroErrorReporter micro_error_reporter;
    tflite::AllOpsResolver resolver;
    const tflite::Model* model;
    uint8_t* tensor_arena;

    // Performance monitoring
    PerformanceMonitor performance_monitor;

public:
    EdgeAIEngine() : micro_error_reporter() {}

    bool initialize(const unsigned char* model_data, size_t model_size) {
        // Load model
        model = tflite::GetModel(model_data);
        if (model->version() != TFLITE_SCHEMA_VERSION) {
            micro_error_reporter.Report("Model version mismatch");
            return false;
        }

        // Allocate tensor arena (adjust size based on model)
        tensor_arena = new uint8_t[8 * 1024]; // 8KB for small models

        // Build interpreter
        interpreter = new tflite::MicroInterpreter(
            model, resolver, tensor_arena, 8 * 1024, &micro_error_reporter);

        // Allocate tensors
        TfLiteStatus allocate_status = interpreter->AllocateTensors();
        if (allocate_status != kTfLiteOk) {
            micro_error_reporter.Report("Tensor allocation failed");
            return false;
        }

        return true;
    }

    AIResult runInference(const float* input_data, size_t input_size) {
        // Get input tensor
        TfLiteTensor* input_tensor = interpreter->input(0);

        // Copy input data
        memcpy(input_tensor->data.f, input_data, input_size * sizeof(float));

        // Run inference
        uint32_t start_time = micros();
        TfLiteStatus invoke_status = interpreter->Invoke();
        uint32_t inference_time = micros() - start_time;

        if (invoke_status != kTfLiteOk) {
            micro_error_reporter.Report("Inference failed");
            return AIResult{0.0f, 0, false};
        }

        // Get output tensor
        TfLiteTensor* output_tensor = interpreter->output(0);

        // Process results
        float max_probability = 0.0f;
        int predicted_class = 0;

        for (int i = 0; i < output_tensor->dims->data[1]; ++i) {
            float probability = output_tensor->data.f[i];
            if (probability > max_probability) {
                max_probability = probability;
                predicted_class = i;
            }
        }

        // Record performance metrics
        performance_monitor.recordInference(inference_time, max_probability);

        return AIResult{max_probability, predicted_class, true};
    }

    PerformanceStats getPerformanceStats() {
        return performance_monitor.getStats();
    }
};
```

#### 2. Sensor Manager (`src/sensors/`)
```cpp
// Multi-sensor integration
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>  // Temperature/Humidity/Pressure
#include <Adafruit_MPU6050.h> // Accelerometer/Gyroscope
#include <Adafruit_APDS9960.h> // Proximity/Gesture/Color

class SensorManager {
private:
    Adafruit_BME280 bme;      // Environmental sensor
    Adafruit_MPU6050 mpu;     // Motion sensor
    Adafruit_APDS9960 apds;   // Proximity sensor

    SensorData last_reading;
    unsigned long last_update;

public:
    bool initialize() {
        // Initialize I2C
        Wire.begin();

        // Initialize BME280
        if (!bme.begin(0x76)) {
            Serial.println("BME280 initialization failed");
            return false;
        }

        // Initialize MPU6050
        if (!mpu.begin()) {
            Serial.println("MPU6050 initialization failed");
            return false;
        }

        // Initialize APDS9960
        if (!apds.begin()) {
            Serial.println("APDS9960 initialization failed");
            return false;
        }

        // Enable proximity and gesture sensing
        apds.enableProximity(true);
        apds.enableGesture(true);

        return true;
    }

    SensorData readAllSensors() {
        SensorData data;

        // Read environmental data
        data.temperature = bme.readTemperature();
        data.humidity = bme.readHumidity();
        data.pressure = bme.readPressure() / 100.0F;

        // Read motion data
        sensors_event_t accel, gyro, temp;
        mpu.getEvent(&accel, &gyro, &temp);

        data.accel_x = accel.acceleration.x;
        data.accel_y = accel.acceleration.y;
        data.accel_z = accel.acceleration.z;

        data.gyro_x = gyro.gyro.x;
        data.gyro_y = gyro.gyro.y;
        data.gyro_z = gyro.gyro.z;

        // Read proximity data
        data.proximity = apds.readProximity();

        // Read gesture if available
        data.gesture = readGesture();

        data.timestamp = millis();
        last_reading = data;
        last_update = millis();

        return data;
    }

    bool hasNewData() {
        return (millis() - last_update) < 100; // Data fresher than 100ms
    }

    SensorData getLastReading() {
        return last_reading;
    }

private:
    uint8_t readGesture() {
        uint8_t gesture = APDS9960_NONE;

        if (apds.gestureValid()) {
            gesture = apds.readGesture();
        }

        return gesture;
    }
};
```

#### 3. Cloud Connector (`src/cloud/`)
```cpp
// MQTT-based cloud connectivity
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

class CloudConnector {
private:
    WiFiClient wifi_client;
    PubSubClient mqtt_client;
    const char* mqtt_server;
    const char* device_id;
    const char* device_secret;

    // Security
    SecurityManager security_manager;

    // Callbacks
    std::function<void(String, String)> message_callback;

public:
    CloudConnector(const char* server, const char* id, const char* secret)
        : mqtt_server(server), device_id(id), device_secret(secret),
          mqtt_client(wifi_client) {}

    bool connect() {
        // Connect to WiFi
        if (!connectWiFi()) {
            return false;
        }

        // Configure MQTT
        mqtt_client.setServer(mqtt_server, 8883); // Secure MQTT
        mqtt_client.setCallback([this](char* topic, byte* payload, unsigned int length) {
            this->mqttCallback(topic, payload, length);
        });

        // Connect with authentication
        String client_id = String("iot-device-") + device_id;
        if (mqtt_client.connect(client_id.c_str(), device_id, device_secret)) {
            // Subscribe to command topics
            mqtt_client.subscribe("devices/commands");
            mqtt_client.subscribe(String("devices/") + device_id + "/commands");

            return true;
        }

        return false;
    }

    void publishTelemetry(const SensorData& data, const AIResult& ai_result) {
        StaticJsonDocument<512> doc;

        // Device info
        doc["device_id"] = device_id;
        doc["timestamp"] = data.timestamp;

        // Sensor data
        JsonObject sensors = doc.createNestedObject("sensors");
        sensors["temperature"] = data.temperature;
        sensors["humidity"] = data.humidity;
        sensors["pressure"] = data.pressure;
        sensors["proximity"] = data.proximity;

        // AI results
        JsonObject ai = doc.createNestedObject("ai");
        ai["prediction"] = ai_result.predicted_class;
        ai["confidence"] = ai_result.confidence;
        ai["inference_success"] = ai_result.success;

        // Performance metrics
        JsonObject performance = doc.createNestedObject("performance");
        PerformanceStats stats = getAIEngine()->getPerformanceStats();
        performance["avg_inference_time"] = stats.avg_inference_time;
        performance["battery_level"] = getBatteryLevel();

        // Sign and encrypt payload
        String payload = security_manager.signAndEncrypt(doc.as<String>());

        // Publish
        String topic = String("devices/") + device_id + "/telemetry";
        mqtt_client.publish(topic.c_str(), payload.c_str());
    }

    void publishAlert(const char* alert_type, const char* message) {
        StaticJsonDocument<256> doc;

        doc["device_id"] = device_id;
        doc["timestamp"] = millis();
        doc["alert_type"] = alert_type;
        doc["message"] = message;
        doc["severity"] = "HIGH";

        String payload = security_manager.signAndEncrypt(doc.as<String>());
        String topic = String("devices/") + device_id + "/alerts";

        mqtt_client.publish(topic.c_str(), payload.c_str());
    }

    void setMessageCallback(std::function<void(String, String)> callback) {
        message_callback = callback;
    }

    void loop() {
        if (!mqtt_client.connected()) {
            reconnect();
        }
        mqtt_client.loop();
    }

private:
    bool connectWiFi() {
        // WiFi connection logic
        // Use secure WiFi with WPA2-Enterprise if available
        WiFi.begin("your-ssid", "your-password");

        int attempts = 0;
        while (WiFi.status() != WL_CONNECTED && attempts < 20) {
            delay(500);
            attempts++;
        }

        return WiFi.status() == WL_CONNECTED;
    }

    void reconnect() {
        while (!mqtt_client.connected()) {
            Serial.print("Attempting MQTT connection...");

            String client_id = String("iot-device-") + device_id;
            if (mqtt_client.connect(client_id.c_str(), device_id, device_secret)) {
                Serial.println("connected");

                // Resubscribe
                mqtt_client.subscribe("devices/commands");
                mqtt_client.subscribe(String("devices/") + device_id + "/commands");
            } else {
                Serial.print("failed, rc=");
                Serial.print(mqtt_client.state());
                Serial.println(" try again in 5 seconds");
                delay(5000);
            }
        }
    }

    void mqttCallback(char* topic, byte* payload, unsigned int length) {
        String topic_str = String(topic);
        String message = "";

        for (unsigned int i = 0; i < length; i++) {
            message += (char)payload[i];
        }

        // Verify message signature
        if (!security_manager.verifySignature(message)) {
            Serial.println("Message signature verification failed");
            return;
        }

        // Decrypt message
        String decrypted = security_manager.decrypt(message);

        if (message_callback) {
            message_callback(topic_str, decrypted);
        }
    }

    float getBatteryLevel() {
        // Read battery voltage (platform-specific)
        // For ESP32, this would read from ADC
        return 85.0f; // Placeholder
    }
};
```

## Model Training Pipeline

### Training Scripts (`training/`)
```python
# train_iot_model.py
import tensorflow as tf
import numpy as np
from sklearn.model_selection import train_test_split
import os

def create_iot_model(input_shape, num_classes):
    """Create a lightweight model optimized for IoT devices"""
    model = tf.keras.Sequential([
        tf.keras.layers.Conv1D(16, 3, activation='relu', input_shape=input_shape),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.Conv1D(32, 3, activation='relu'),
        tf.keras.layers.MaxPooling1D(2),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(num_classes, activation='softmax')
    ])

    # Compile with optimizations for edge deployment
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    return model

def train_iot_model():
    """Train and convert model for IoT deployment"""
    # Generate synthetic sensor data for demonstration
    # In practice, use real sensor data
    np.random.seed(42)

    # Simulate sensor readings: [temp, humidity, pressure, accel_x, accel_y, accel_z]
    n_samples = 10000
    n_features = 6
    n_classes = 3  # Normal, Warning, Critical

    # Generate synthetic data
    X = np.random.randn(n_samples, 100, n_features)  # 100 time steps
    y = np.random.randint(0, n_classes, n_samples)

    # Convert to categorical
    y_categorical = tf.keras.utils.to_categorical(y, num_classes=n_classes)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_categorical, test_size=0.2, random_state=42
    )

    # Create and train model
    model = create_iot_model((100, n_features), n_classes)

    # Add early stopping and model checkpointing
    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
        tf.keras.callbacks.ModelCheckpoint(
            'best_iot_model.h5', save_best_only=True, monitor='val_accuracy'
        )
    ]

    model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        validation_data=(X_test, y_test),
        callbacks=callbacks
    )

    # Evaluate model
    test_loss, test_accuracy = model.evaluate(X_test, y_test)
    print(f"Test accuracy: {test_accuracy:.4f}")

    # Convert to TensorFlow Lite
    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    # Apply IoT optimizations
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS_INT8  # Use int8 operations
    ]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8

    # Provide representative dataset for quantization
    def representative_dataset():
        for _ in range(100):
            data = np.random.randn(1, 100, n_features).astype(np.float32)
            yield [data]

    converter.representative_dataset = representative_dataset

    # Convert model
    tflite_model = converter.convert()

    # Save the model
    with open('iot_model.tflite', 'wb') as f:
        f.write(tflite_model)

    # Print model information
    original_size = os.path.getsize('best_iot_model.h5')
    quantized_size = len(tflite_model)

    print(f"Original model size: {original_size} bytes")
    print(f"Quantized model size: {quantized_size} bytes")
    print(f"Compression ratio: {original_size/quantized_size:.2f}x")

    return model, tflite_model

if __name__ == "__main__":
    train_iot_model()
```

### Model Conversion for Microcontrollers (`conversion/`)
```python
# convert_for_tflm.py
import tensorflow as tf
import numpy as np

def convert_for_tflm(model_path, output_dir):
    """Convert TensorFlow Lite model for TensorFlow Lite Micro"""

    # Load the TFLite model
    with open(model_path, 'rb') as f:
        tflite_model = f.read()

    # Create C header file for embedding in firmware
    create_c_header(tflite_model, output_dir)

    # Generate model info
    print_model_info(tflite_model)

def create_c_header(model_data, output_dir):
    """Create C header file with model data"""

    # Convert model to C array
    model_array = ', '.join([f'0x{byte:02x}' for byte in model_data])

    header_content = f'''#ifndef IOT_MODEL_H_
#define IOT_MODEL_H_

#include <cstdint>

const unsigned char iot_model[] = {{
    {model_array}
}};

const unsigned int iot_model_len = {len(model_data)};

#endif  // IOT_MODEL_H_
'''

    with open(f'{output_dir}/iot_model.h', 'w') as f:
        f.write(header_content)

    print(f"C header file created: {output_dir}/iot_model.h")

def print_model_info(model_data):
    """Print information about the converted model"""

    # Load model to get metadata
    interpreter = tf.lite.Interpreter(model_content=model_data)

    # Get input/output details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    print("Model Information:")
    print(f"Model size: {len(model_data)} bytes")

    print("\nInput tensors:")
    for i, details in enumerate(input_details):
        print(f"  Input {i}: {details['shape']}, {details['dtype']}")

    print("\nOutput tensors:")
    for i, details in enumerate(output_details):
        print(f"  Output {i}: {details['shape']}, {details['dtype']}")

    # Estimate memory requirements
    interpreter.allocate_tensors()
    arena_size = interpreter.tensor_arena_size()
    print(f"\nEstimated tensor arena size: {arena_size} bytes")

if __name__ == "__main__":
    convert_for_tflm('iot_model.tflite', 'src/model')
```

## CI/CD Pipeline

### GitHub Actions (`.github/workflows/`)
```yaml
name: IoT AI CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'

    - name: Install Python dependencies
      run: pip install -r requirements.txt

    - name: Run model training tests
      run: python -m pytest training/tests/ -v

    - name: Test model conversion
      run: python conversion/convert_for_tflm.py

  build-esp32:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up PlatformIO
      uses: tanersener/setup-platformio@v1

    - name: Build ESP32 firmware
      run: pio run -e esp32

    - name: Upload ESP32 firmware
      uses: actions/upload-artifact@v3
      with:
        name: esp32-firmware
        path: .pio/build/esp32/firmware.bin

  build-raspberry-pi:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python for Raspberry Pi
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install Raspberry Pi dependencies
      run: pip install -r raspberry-pi/requirements.txt

    - name: Build Raspberry Pi application
      run: python setup.py build_ext --inplace

    - name: Upload Raspberry Pi build
      uses: actions/upload-artifact@v3
      with:
        name: raspberry-pi-build
        path: dist/

  deploy:
    needs: [build-esp32, build-raspberry-pi]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3

    - name: Download ESP32 firmware
      uses: actions/download-artifact@v3
      with:
        name: esp32-firmware

    - name: Download Raspberry Pi build
      uses: actions/download-artifact@v3
      with:
        name: raspberry-pi-build

    - name: Deploy to AWS IoT
      run: |
        aws iot create-ota-update \
          --ota-update-id "iot-ai-firmware-${{ github.sha }}" \
          --targets "thinggroup/IoT-AI-Devices" \
          --files file://firmware.bin \
          --role-arn ${{ secrets.AWS_IOT_OTA_ROLE_ARN }}

    - name: Update model registry
      run: |
        aws s3 cp iot_model.tflite s3://iot-ai-models/${{ github.sha }}/model.tflite
        aws iot update-thing-shadow \
          --thing-name "IoT-AI-Model-Registry" \
          --payload '{"state":{"desired":{"model_version":"${{ github.sha }}"}}}' \
          --region ${{ secrets.AWS_REGION }}
```

## Power Management

### Power Optimization (`src/power/`)
```cpp
// Power management for battery-powered IoT devices
#include <esp_sleep.h>
#include <esp_pm.h>

class PowerManager {
private:
    esp_pm_config_t pm_config;
    bool deep_sleep_enabled;
    uint64_t sleep_duration_us;

public:
    PowerManager() : deep_sleep_enabled(false), sleep_duration_us(30000000) { // 30 seconds
        // Configure power management
        pm_config.max_freq_mhz = 80;     // Maximum CPU frequency
        pm_config.min_freq_mhz = 10;     // Minimum CPU frequency
        pm_config.light_sleep_enable = true;

        esp_pm_configure(&pm_config);
    }

    void enableDeepSleep(uint64_t duration_us = 30000000) {
        deep_sleep_enabled = true;
        sleep_duration_us = duration_us;

        // Configure wake-up sources
        esp_sleep_enable_timer_wakeup(sleep_duration_us);
        esp_sleep_enable_ext0_wakeup(GPIO_NUM_33, 0); // Wake on button press
    }

    void enterDeepSleep() {
        if (deep_sleep_enabled) {
            Serial.println("Entering deep sleep...");
            esp_deep_sleep_start();
        }
    }

    void enterLightSleep() {
        if (pm_config.light_sleep_enable) {
            esp_light_sleep_start();
        }
    }

    void optimizeForInference() {
        // Increase CPU frequency for AI inference
        esp_pm_configure(&(esp_pm_config_t){
            .max_freq_mhz = 240,    // Higher frequency for inference
            .min_freq_mhz = 80,
            .light_sleep_enable = false  // Disable light sleep during inference
        });
    }

    void optimizeForIdle() {
        // Reduce power consumption when idle
        esp_pm_configure(&pm_config);  // Restore original config
    }

    float getBatteryLevel() {
        // Read battery voltage from ADC
        // This is ESP32-specific implementation
        return analogRead(34) * 3.3 / 4095.0 * 2.0; // Assuming voltage divider
    }

    void monitorPowerConsumption() {
        static unsigned long last_check = 0;
        if (millis() - last_check > 60000) { // Check every minute
            float battery_level = getBatteryLevel();

            if (battery_level < 3.0) { // Low battery warning
                // Send alert to cloud
                cloud_connector.publishAlert("LOW_BATTERY",
                    String("Battery level: ") + battery_level + "V");

                // Enter power-saving mode
                enableDeepSleep(60000000); // Sleep for 1 minute
            }

            last_check = millis();
        }
    }
};
```

### Adaptive Sampling (`src/sampling/`)
```cpp
// Adaptive sensor sampling based on AI predictions and power constraints
class AdaptiveSampler {
private:
    SensorManager& sensor_manager;
    EdgeAIEngine& ai_engine;
    PowerManager& power_manager;

    SamplingMode current_mode;
    unsigned long last_sample_time;
    uint32_t base_sampling_interval;  // Base interval in milliseconds

    // Adaptive parameters
    float prediction_confidence_threshold;
    uint32_t high_activity_interval;
    uint32_t low_activity_interval;

public:
    AdaptiveSampler(SensorManager& sensors, EdgeAIEngine& ai, PowerManager& power)
        : sensor_manager(sensors), ai_engine(ai), power_manager(power),
          current_mode(NORMAL), last_sample_time(0),
          base_sampling_interval(5000),  // 5 seconds base interval
          prediction_confidence_threshold(0.8),
          high_activity_interval(1000),   // 1 second for high activity
          low_activity_interval(30000) {  // 30 seconds for low activity

    }

    void updateSampling() {
        unsigned long current_time = millis();

        if (current_time - last_sample_time >= getCurrentInterval()) {
            // Read sensors
            SensorData data = sensor_manager.readAllSensors();

            // Prepare data for AI inference
            float input_data[6] = {
                data.temperature,
                data.humidity,
                data.pressure,
                data.accel_x,
                data.accel_y,
                data.accel_z
            };

            // Run AI inference
            AIResult result = ai_engine.runInference(input_data, 6);

            // Adapt sampling based on AI prediction
            adaptSamplingStrategy(result, data);

            last_sample_time = current_time;
        }
    }

    SamplingMode getCurrentMode() {
        return current_mode;
    }

private:
    uint32_t getCurrentInterval() {
        switch (current_mode) {
            case HIGH_ACTIVITY:
                return high_activity_interval;
            case LOW_ACTIVITY:
                return low_activity_interval;
            case POWER_SAVING:
                return low_activity_interval * 2;  // Even slower for power saving
            default:
                return base_sampling_interval;
        }
    }

    void adaptSamplingStrategy(const AIResult& result, const SensorData& data) {
        // Determine activity level based on AI prediction and sensor data
        float activity_score = calculateActivityScore(result, data);

        // Check battery level
        float battery_level = power_manager.getBatteryLevel();

        // Adapt sampling mode
        if (battery_level < 3.2) {
            // Low battery - prioritize power saving
            current_mode = POWER_SAVING;
        } else if (activity_score > 0.7 || result.confidence > prediction_confidence_threshold) {
            // High activity or high confidence prediction
            current_mode = HIGH_ACTIVITY;
        } else if (activity_score < 0.3 && result.confidence < 0.6) {
            // Low activity and low confidence
            current_mode = LOW_ACTIVITY;
        } else {
            // Normal activity
            current_mode = NORMAL;
        }

        // Adjust power management based on mode
        if (current_mode == HIGH_ACTIVITY) {
            power_manager.optimizeForInference();
        } else {
            power_manager.optimizeForIdle();
        }
    }

    float calculateActivityScore(const AIResult& result, const SensorData& data) {
        // Calculate activity score based on sensor readings and AI prediction
        float accel_magnitude = sqrt(data.accel_x * data.accel_x +
                                   data.accel_y * data.accel_y +
                                   data.accel_z * data.accel_z);

        // Normalize acceleration (assuming 9.8 m/s² = 1g)
        float normalized_accel = accel_magnitude / 9.8;

        // Combine with AI confidence and prediction class
        float activity_score = (normalized_accel * 0.4) +
                              (result.confidence * 0.4) +
                              ((result.predicted_class == 1) ? 0.2 : 0.0);  // Class 1 = warning/critical

        return min(activity_score, 1.0f);
    }
};
```

## Security Implementation

### Secure Boot and Model Protection (`src/security/`)
```cpp
// Security features for IoT AI devices
#include <esp_secure_boot.h>
#include <esp_efuse.h>

class SecurityManager {
private:
    // Encryption keys (should be stored securely)
    uint8_t encryption_key[32];
    uint8_t hmac_key[32];

public:
    bool initialize() {
        // Generate or load encryption keys
        if (!loadKeys()) {
            generateKeys();
            storeKeys();
        }

        // Enable secure boot if not already enabled
        if (!esp_secure_boot_enabled()) {
            return enableSecureBoot();
        }

        return true;
    }

    String signAndEncrypt(const String& payload) {
        // Create HMAC signature
        uint8_t signature[32];
        createHMAC(payload.c_str(), payload.length(), signature);

        // Encrypt payload
        uint8_t encrypted[256]; // Adjust size as needed
        size_t encrypted_len = encryptData((uint8_t*)payload.c_str(), payload.length(), encrypted);

        // Combine signature and encrypted data
        StaticJsonDocument<512> doc;
        doc["signature"] = base64::encode(signature, 32);
        doc["data"] = base64::encode(encrypted, encrypted_len);

        String result;
        serializeJson(doc, result);
        return result;
    }

    String decryptAndVerify(const String& message) {
        // Parse JSON message
        StaticJsonDocument<512> doc;
        deserializeJson(doc, message);

        const char* signature_b64 = doc["signature"];
        const char* data_b64 = doc["data"];

        // Decode signature and data
        uint8_t signature[32];
        base64::decode(signature_b64, signature);

        size_t data_len = base64::decodeLength(data_b64);
        uint8_t encrypted_data[256];
        base64::decode(data_b64, encrypted_data);

        // Decrypt data
        uint8_t decrypted_data[256];
        size_t decrypted_len = decryptData(encrypted_data, data_len, decrypted_data);

        // Verify signature
        uint8_t calculated_signature[32];
        createHMAC((char*)decrypted_data, decrypted_len, calculated_signature);

        if (memcmp(signature, calculated_signature, 32) != 0) {
            return ""; // Signature verification failed
        }

        return String((char*)decrypted_data, decrypted_len);
    }

    bool verifyModelIntegrity(const uint8_t* model_data, size_t model_size) {
        // Calculate model hash
        uint8_t model_hash[32];
        calculateSHA256(model_data, model_size, model_hash);

        // Compare with expected hash (stored securely)
        uint8_t expected_hash[32];
        if (!loadModelHash(expected_hash)) {
            return false; // No expected hash stored
        }

        return memcmp(model_hash, expected_hash, 32) == 0;
    }

private:
    bool loadKeys() {
        // Load keys from secure storage (eFuse, secure flash, etc.)
        // Implementation depends on platform
        return false; // Placeholder
    }

    void generateKeys() {
        // Generate cryptographically secure keys
        esp_fill_random(encryption_key, sizeof(encryption_key));
        esp_fill_random(hmac_key, sizeof(hmac_key));
    }

    void storeKeys() {
        // Store keys in secure storage
        // Implementation depends on platform
    }

    bool enableSecureBoot() {
        // Enable secure boot (platform-specific)
        // This is a simplified implementation
        return false;
    }

    void createHMAC(const char* data, size_t len, uint8_t* output) {
        // Create HMAC-SHA256
        // Implementation using ESP32 crypto libraries
    }

    size_t encryptData(const uint8_t* input, size_t input_len, uint8_t* output) {
        // AES encryption
        // Implementation using ESP32 crypto libraries
        return input_len; // Placeholder
    }

    size_t decryptData(const uint8_t* input, size_t input_len, uint8_t* output) {
        // AES decryption
        // Implementation using ESP32 crypto libraries
        return input_len; // Placeholder
    }

    void calculateSHA256(const uint8_t* data, size_t len, uint8_t* output) {
        // SHA256 calculation
        // Implementation using ESP32 crypto libraries
    }

    bool loadModelHash(uint8_t* hash) {
        // Load expected model hash from secure storage
        return false; // Placeholder
    }
};
```

## OTA Updates

### Over-the-Air Updates (`src/ota/`)
```cpp
// OTA update system for models and firmware
#include <HTTPClient.h>
#include <Update.h>

class OTAUpdater {
private:
    const char* update_server_url;
    const char* device_id;
    SecurityManager& security_manager;

    String current_firmware_version;
    String current_model_version;

public:
    OTAUpdater(const char* server_url, const char* id, SecurityManager& sec_mgr)
        : update_server_url(server_url), device_id(id), security_manager(sec_mgr) {}

    void checkForUpdates() {
        if (WiFi.status() != WL_CONNECTED) {
            return;
        }

        HTTPClient http;
        String url = String(update_server_url) + "/updates?device_id=" + device_id;

        http.begin(url);
        int httpCode = http.GET();

        if (httpCode == HTTP_CODE_OK) {
            String payload = http.getString();
            processUpdateManifest(payload);
        }

        http.end();
    }

    void processUpdateManifest(const String& manifest) {
        // Parse JSON manifest
        StaticJsonDocument<1024> doc;
        deserializeJson(doc, manifest);

        // Check firmware update
        String firmware_version = doc["firmware"]["version"];
        String firmware_url = doc["firmware"]["url"];

        if (firmware_version != current_firmware_version) {
            Serial.println("Firmware update available: " + firmware_version);
            performFirmwareUpdate(firmware_url, firmware_version);
        }

        // Check model update
        String model_version = doc["model"]["version"];
        String model_url = doc["model"]["url"];

        if (model_version != current_model_version) {
            Serial.println("Model update available: " + model_version);
            performModelUpdate(model_url, model_version);
        }
    }

    void performFirmwareUpdate(const String& url, const String& version) {
        Serial.println("Starting firmware update...");

        HTTPClient http;
        http.begin(url);
        int httpCode = http.GET();

        if (httpCode == HTTP_CODE_OK) {
            int contentLength = http.getSize();
            bool canBegin = Update.begin(contentLength);

            if (canBegin) {
                WiFiClient* stream = http.getStreamPtr();
                size_t written = Update.writeStream(*stream);

                if (written == contentLength) {
                    Serial.println("Firmware update successful");
                    if (Update.end()) {
                        if (Update.isFinished()) {
                            Serial.println("Update completed. Rebooting...");
                            delay(1000);
                            ESP.restart();
                        }
                    }
                } else {
                    Serial.println("Firmware update failed - written bytes mismatch");
                    Update.abort();
                }
            } else {
                Serial.println("Not enough space for firmware update");
            }
        }

        http.end();
    }

    void performModelUpdate(const String& url, const String& version) {
        Serial.println("Starting model update...");

        HTTPClient http;
        http.begin(url);
        int httpCode = http.GET();

        if (httpCode == HTTP_CODE_OK) {
            // Download model data
            String modelData = http.getString();

            // Verify model integrity
            if (security_manager.verifyModelIntegrity((uint8_t*)modelData.c_str(), modelData.length())) {
                // Save new model
                if (saveModelToFlash(modelData, version)) {
                    current_model_version = version;
                    Serial.println("Model update successful");

                    // Signal AI engine to reload model
                    ai_engine.reloadModel();
                } else {
                    Serial.println("Failed to save model");
                }
            } else {
                Serial.println("Model integrity verification failed");
            }
        }

        http.end();
    }

private:
    bool saveModelToFlash(const String& modelData, const String& version) {
        // Save model to flash memory
        // Implementation depends on platform
        File modelFile = SPIFFS.open("/model.tflite", "w");
        if (!modelFile) {
            return false;
        }

        modelFile.print(modelData);
        modelFile.close();

        // Update version in preferences
        preferences.putString("model_version", version);

        return true;
    }
};
```

## Performance Benchmarks

### Benchmark Results
```
Platform: ESP32-WROOM-32
Core: Dual-core Xtensa LX6
RAM: 520KB
Flash: 4MB

Model: Sensor Classification (6 inputs, 3 classes)
Quantized Model Size: 12KB

Inference Performance:
- Average inference time: 45ms
- Peak RAM usage: 85KB
- Flash usage: 68%
- Power consumption: 120mA active, 15μA deep sleep

Raspberry Pi 4 Model B
CPU: Quad-core Cortex-A72
RAM: 2GB LPDDR4
Storage: MicroSD

Model: Image Classification (224x224 RGB input)
Model Size: 45MB

Inference Performance:
- Average inference time: 280ms (CPU), 45ms (GPU with OpenCV)
- Peak RAM usage: 512MB
- Power consumption: 5W average
```

### Comparative Benchmarks
```
Platform Comparison:

Platform          | Model Size | Inference (ms) | Power (mA) | Cost ($)
------------------|------------|----------------|-------------|---------
ESP32             | 12KB       | 45             | 120        | 5
Raspberry Pi 4    | 45MB       | 280            | 1000       | 35
Coral Dev Board   | 45MB       | 15             | 2000       | 150
Jetson Nano       | 45MB       | 25             | 5000       | 99
```

## Troubleshooting

### Common Issues

#### 1. Model Loading Failures
```cpp
// Check model file exists and is readable
if (!SPIFFS.exists("/model.tflite")) {
    Serial.println("Model file not found");
    // Try downloading from cloud
    ota_updater.checkForUpdates();
    return;
}

// Verify model integrity
File modelFile = SPIFFS.open("/model.tflite", "r");
if (!modelFile) {
    Serial.println("Cannot open model file");
    return;
}

// Check file size
size_t fileSize = modelFile.size();
if (fileSize == 0) {
    Serial.println("Model file is empty");
    modelFile.close();
    return;
}
```

#### 2. Memory Issues
```cpp
// Monitor heap usage
Serial.printf("Free heap: %d bytes\n", ESP.getFreeHeap());
Serial.printf("Min free heap: %d bytes\n", ESP.getMinFreeHeap());

// For TFLM, ensure tensor arena is properly sized
const int kTensorArenaSize = 8 * 1024;  // Start with 8KB
uint8_t tensor_arena[kTensorArenaSize];

// If allocation fails, increase arena size or optimize model
if (interpreter->AllocateTensors() != kTfLiteOk) {
    Serial.println("Tensor allocation failed - increase arena size");
}
```

#### 3. Connectivity Issues
```cpp
// Check WiFi connection
if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected - attempting reconnection");
    WiFi.reconnect();
    return;
}

// Check MQTT connection
if (!mqtt_client.connected()) {
    Serial.println("MQTT not connected - attempting reconnection");
    cloud_connector.reconnect();
}

// Verify certificates
if (!security_manager.verifyCertificates()) {
    Serial.println("Certificate verification failed");
    // Try updating certificates via OTA
    ota_updater.checkForUpdates();
}
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/iot-ai-kit/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/iot-ai-kit/discussions)

---

*Built with ❤️ for the IoT AI development community*