import torch
from transformers import AutoTokenizer, AutoModel

SEQ_LEN = 16

tokenizer = AutoTokenizer.from_pretrained(
    "sentence-transformers/all-MiniLM-L6-v2"
)
model = AutoModel.from_pretrained(
    "sentence-transformers/all-MiniLM-L6-v2"
)
model.eval()

dummy = tokenizer(
    "test sentence",
    return_tensors="pt",
    padding="max_length",
    truncation=True,
    max_length=SEQ_LEN
)

torch.onnx.export(
    model,
    (dummy["input_ids"], dummy["attention_mask"]),
    "minilm_static.onnx",
    input_names=["input_ids", "attention_mask"],
    output_names=["output"],
    opset_version=18
)

print("Static ONNX exported")
