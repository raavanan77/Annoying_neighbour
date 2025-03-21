#include <stdio.h>
#include <stdlib.h>
#include <tensorflow/lite/model.h>
#include <tensorflow/lite/interpreter.h>
#include <tensorflow/lite/kernels/register.h>
#include <tensorflow/lite/string_type.h>
#include <tensorflow/lite/version.h>

int main() {
    // Load TensorFlow Lite model
    const char* model_path = "model.tflite";
    TfLiteModel* model = TfLiteModelCreateFromFile(model_path);
    if (model == NULL) {
        printf("Failed to load model from file: %s\n", model_path);
        return -1;
    }

    // Create an interpreter
    TfLiteInterpreterOptions* options = TfLiteInterpreterOptionsCreate();
    TfLiteInterpreter* interpreter = TfLiteInterpreterCreate(model, options);
    if (interpreter == NULL) {
        printf("Failed to create interpreter\n");
        TfLiteModelDelete(model);
        return -1;
    }

    // Allocate tensors (this prepares the interpreter to run inference)
    if (TfLiteInterpreterAllocateTensors(interpreter) != kTfLiteOk) {
        printf("Failed to allocate tensors\n");
        TfLiteInterpreterDelete(interpreter);
        TfLiteModelDelete(model);
        return -1;
    }

    // Get input tensor
    TfLiteTensor* input_tensor = TfLiteInterpreterGetInputTensor(interpreter, 0);
    if (input_tensor == NULL) {
        printf("Failed to get input tensor\n");
        TfLiteInterpreterDelete(interpreter);
        TfLiteModelDelete(model);
        return -1;
    }

    // Example: Set input data (replace this with your input data)
    // Here, we assume the input tensor is a 1D tensor with shape [1, 4] (like a vector)
    float input_data[4] = {1.0f, 2.0f, 3.0f, 4.0f};
    memcpy(input_tensor->data.f, input_data, sizeof(input_data));

    // Run inference
    if (TfLiteInterpreterInvoke(interpreter) != kTfLiteOk) {
        printf("Failed to invoke the interpreter\n");
        TfLiteInterpreterDelete(interpreter);
        TfLiteModelDelete(model);
        return -1;
    }

    // Get output tensor
    TfLiteTensor* output_tensor = TfLiteInterpreterGetOutputTensor(interpreter, 0);
    if (output_tensor == NULL) {
        printf("Failed to get output tensor\n");
        TfLiteInterpreterDelete(interpreter);
        TfLiteModelDelete(model);
        return -1;
    }

    // Print output data
    // Assuming the output is a 1D tensor (for simplicity)
    printf("Output data: \n");
    for (int i = 0; i < output_tensor->dims->data[0]; i++) {
        printf("%f ", output_tensor->data.f[i]);
    }
    printf("\n");

    // Clean up
    TfLiteInterpreterDelete(interpreter);
    TfLiteModelDelete(model);
    return 0;
}
