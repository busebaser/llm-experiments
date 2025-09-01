# LLM Experiments

Projects and experiments on Large Language Models (LLMs), including GPT-2 fine-tuning, text classification, and instruction-tuned personal assistants.

---

## Files Overview

- **`gpt_download.py`**  
  A utility script for downloading pre-trained GPT-2 models from OpenAI’s storage.  
  It loads the TensorFlow checkpoint files and converts them into NumPy arrays for later use in PyTorch.  

- **`gptModel.py`**  
  A PyTorch implementation of the GPT architecture built from scratch.  
  Includes:
  - Multi-head attention
  - Transformer blocks
  - Feed-forward layers
  - Custom layer normalization
  - A configurable GPT model constructor

- **`my_gpt2.ipynb`**  
  A Jupyter notebook demonstrating how to build and test the GPT-2 model using the components from `gptModel.py`.  
  Useful for experimenting with language modeling tasks.

- **`spam_classifier_gpt.ipynb`**  
  A Jupyter notebook for adapting GPT-2 to a **binary text classification task** (spam detection).  
  - The GPT-2 backbone is used as a feature extractor.  
  - The original language modeling head is replaced with a linear classification head (`embedding_dim → 2`).  
  - Trained on the [SMS Spam Collection dataset](https://archive.ics.uci.edu/dataset/228/sms+spam+collection).

---
