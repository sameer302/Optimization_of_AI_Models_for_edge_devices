import onnxruntime as ort
import numpy as np

session = ort.InferenceSession("minilm.onnx")

inputs = {
    "input_ids": np.ones((1, 16), dtype=np.int64),
    "attention_mask": np.ones((1, 16), dtype=np.int64),
}

outputs = session.run(None, inputs)
print(outputs[0].shape)