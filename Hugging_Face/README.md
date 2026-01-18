# Hugging Face Projects

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Transformers](https://img.shields.io/badge/Transformers-Latest-yellow.svg)](https://huggingface.co/transformers/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org/)

Scripts and notebooks leveraging the Hugging Face ecosystem (Transformers, Datasets, etc.) for NLP and ML tasks.

## Project Structure

```
Hugging_Face/
├── scripts/
│   ├── pulling_gpt_model_from_hugging_face.ipynb  # GPT model loading tutorial
│   └── text_to_speech.ipynb                        # TTS implementation
├── output files/                                    # Generated outputs
├── .gitignore
└── README.md
```

## Scripts Overview

| Script | Description | Models Used |
|--------|-------------|-------------|
| `pulling_gpt_model_from_hugging_face.ipynb` | Loading and using GPT models | GPT-2, GPT-Neo |
| `text_to_speech.ipynb` | Text-to-Speech synthesis | TTS models |

## Prerequisites

- Python 3.8 or higher
- CUDA-compatible GPU (recommended for large models)
- Jupyter Notebook or JupyterLab

## Installation

1. Navigate to this directory:
   ```bash
   cd Hugging_Face
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) For GPU support:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

## Usage

### Running Notebooks

1. Start Jupyter:
   ```bash
   jupyter notebook
   ```

2. Navigate to `scripts/` and open the desired notebook

### GPT Model Example
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

inputs = tokenizer("Hello, I am", return_tensors="pt")
outputs = model.generate(**inputs, max_length=50)
print(tokenizer.decode(outputs[0]))
```

## Model Download Notes

- Models are cached in `~/.cache/huggingface/` by default
- First run will download models (can be several GB)
- Use `TRANSFORMERS_CACHE` env variable to change cache location
- For offline use, download models in advance:
  ```bash
  python -c "from transformers import AutoModel; AutoModel.from_pretrained('gpt2')"
  ```

## Memory Requirements

| Model | RAM Required | GPU VRAM |
|-------|--------------|----------|
| GPT-2 (small) | 2 GB | 2 GB |
| GPT-2 (medium) | 4 GB | 4 GB |
| GPT-Neo 1.3B | 8 GB | 6 GB |

## Configuration

Set Hugging Face token for gated models:
```bash
export HF_TOKEN=your_huggingface_token
```

Or in Python:
```python
from huggingface_hub import login
login(token="your_token")
```

## License

This project is part of [Gen-AI-Projects](../README.md) and is licensed under the MIT License.
