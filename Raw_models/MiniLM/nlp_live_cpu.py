import time
import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer

# Load tokenizer (CPU)
tokenizer = AutoTokenizer.from_pretrained(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# Load ONNX model (CPU)
session = ort.InferenceSession("minilm.onnx")

def embed(text):
    tokens = tokenizer(
        text,
        return_tensors="np",
        padding="max_length",
        truncation=True,
        max_length=16
    )

    t0 = time.perf_counter()

    outputs = session.run(
        None,
        {
            "input_ids": tokens["input_ids"],
            "attention_mask": tokens["attention_mask"]
        }
    )

    t1 = time.perf_counter()

    embedding = outputs[0].mean(axis=1)[0]
    latency_ms = (t1 - t0) * 1000

    return embedding, latency_ms

def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print("\n=== MiniLM Live Demo (CPU) ===\n")

ref_text = input("Reference text: ")
ref_emb, ref_time = embed(ref_text)

print(f"Reference inference time: {ref_time:.2f} ms\n")

while True:
    text = input("Compare with (or 'exit'): ")
    if text.lower() == "exit":
        break

    emb, latency = embed(text)
    sim = cosine(ref_emb, emb)

    print(f"Similarity: {sim:.3f}")
    print(f"Inference time (CPU): {latency:.2f} ms\n")
