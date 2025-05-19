# 🐑 WEB-SHEPHERD: Advancin Process Reward Models for Web Agents

[![Paper](https://img.shields.io/badge/Paper-NeurIPS--2025-informational)](https://openreview.net/forum?id=YOUR_ID)
[![Hugging Face Demo](https://img.shields.io/badge/Demo-HuggingFace-blue)](https://huggingface.co/spaces/WebShepherd/Project-Web-Shepherd)

WEB-SHEPHERD is the **first process reward model (PRM)** designed specifically for web agents. It evaluates trajectories at the step level to provide interpretable and cost-efficient feedback for both learning and inference-time decision making in web navigation tasks.

---

## 🚀 Overview

Recent multimodal language models (MLLMs) have made progress in web automation but struggle with long-horizon planning and cost efficiency. To tackle this, WEB-SHEPHERD introduces:

- **WEBPRM COLLECTION**: A dataset with 40K+ step-level preference annotations and structured checklists.
- **WEBREWARDBENCH**: A benchmark to test PRM effectiveness across diverse web tasks.
- **WEB-SHEPHERD**: A PRM trained to provide step-wise feedback and reward using structured subgoal checklists.

---

## 🧠 Key Features

- ✅ Step-level trajectory evaluation for web agents
- 🧾 Checklist-guided reward modeling for interpretability
- 💰 10× cost reduction compared to prompting GPT-4o
- 📈 Outperforms GPT-4o-mini by **10.9 points** on WebArena-lite
- 🔄 Supports both reward assignment and agent refinement

---

## 📂 Project Structure

```bash
.
├── webshepherd/                 # Source code for the model
│   ├── models/                  # Model architecture & training
│   ├── data/                    # Dataset loading and processing
│   └── inference/               # Inference utilities (e.g., Best-of-n, feedback)
├── scripts/                     # Training & evaluation scripts
├── configs/                     # Model configs and experiment settings
├── data/                        # Downloaded or generated datasets
│   ├── webprm_collection/       # Annotated instructions, checklists, and actions
│   └── webrewardbench/          # Meta-evaluation benchmark
├── demo/                        # Hugging Face Space setup (optional)
├── results/                     # Logs and evaluation outputs
└── README.md
```
