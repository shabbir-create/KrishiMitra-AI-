import json
import tensorflow as tf

# Load TFLite model
interpreter = tf.lite.Interpreter(
    model_path="models/disease_model.tflite"
)

interpreter.allocate_tensors()

# Get input/output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Load disease labels
with open("models/class_names.json", "r", encoding="utf-8") as f:
    class_names = json.load(f)

print("TFLite model loaded successfully!")

print("Input shape:", input_details[0]["shape"])
print("Input dtype:", input_details[0]["dtype"])

print("Output shape:", output_details[0]["shape"])
print("Output dtype:", output_details[0]["dtype"])

print("Total classes:", len(class_names))

assert output_details[0]["shape"][-1] == len(class_names)

print("Model and class labels match!")
