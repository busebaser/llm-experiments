# 📘 Reinforcement Learning & Reasoning Experiments

This folder contains a collection of Jupyter notebooks exploring **classical reinforcement learning problems** and **reasoning experiments with large language models (LLMs)**.  
The aim is both to replicate well-known RL tasks and to investigate how prompting strategies (e.g., Chain-of-Thought) affect model performance.

---

## 🔹 Notebooks

### 1. `classic_rl_problems.ipynb`
- Implements problems from Sutton & Barto’s *Reinforcement Learning: An Introduction*.  
- Includes:
  - **Random Walk**: value prediction with TD(0) vs Monte Carlo.  
  - **Cliff Walking**: policy learning with SARSA vs Q-learning.  
- Focus: Understanding the differences between prediction and control algorithms.

---

### 2. `model_size_vs_cot_accuracy.ipynb`
- Experiments on how **model size** influences reasoning accuracy.  
- Compares small vs larger LLMs on reasoning tasks.  
- Focus: Scaling effects and the role of Chain-of-Thought prompting.

---

### 3. `cot_vs_fewshot_experiments.ipynb`
- Direct comparison of **Zero-shot**, **Few-shot**, and **Chain-of-Thought (CoT)** prompting.  
- Tests performance across reasoning benchmarks.  
- Focus: Which prompting method yields the most accurate answers.

---

## 🚀 How to Use
1. Clone the repository:
   ```bash
   git clone https://github.com/busebaser/llm-experiments.git
