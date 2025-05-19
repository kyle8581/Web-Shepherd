<!-- <p align="left">
  <img src="assets/shepherd_emoji.png" alt="WEB-SHEPHERD Logo" width="100" style="vertical-align: middle; display: inline-block; margin-right: 10px"/>
  <h1 style="font-weight: bold; margin: 0; display: inline-block; vertical-align: middle">Web-Shepherd: Advancing Process Reward Models for Web Agents</h1>
</p> -->
<table>
<tr>
<td><img src="assets/shepherd_emoji.png" alt="WEB-SHEPHERD Logo" width="150"/></td>
<td><h1 style="margin: 0;">Web-Shepherd: Advancing Process Reward Models for Web Agents</h1></td>
</tr>
</table>


<!-- [![Paper](https://img.shields.io/badge/Paper-Preprint-informational?logo=arxiv)](assets/WebShepherd.pdf) -->
<!-- [![arXiv](https://img.shields.io/badge/arXiv-Preprint-red?logo=arxiv)](assets/WebShepherd.pdf) -->
[![PDF](https://img.shields.io/badge/PDF-Preprint-red?logo=arxiv)](assets/WebShepherd.pdf)
[![Model](https://img.shields.io/badge/Model-HuggingFace-informational?logo=huggingface)](https://huggingface.co/WebShepherd/web-shepherd-base)
[![Hugging Face Demo](https://img.shields.io/badge/Demo-Huggingface-blue.svg?logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZlcnNpb249IjEiIHdpZHRoPSI2MDAiIGhlaWdodD0iNjAwIj48cGF0aCBkPSJNMTI5IDExMWMtNTUgNC05MyA2Ni05MyA3OEwwIDM5OGMtMiA3MCAzNiA5MiA2OSA5MWgxYzc5IDAgODctNTcgMTMwLTEyOGgyMDFjNDMgNzEgNTAgMTI4IDEyOSAxMjhoMWMzMyAxIDcxLTIxIDY5LTkxbC0zNi0yMDljMC0xMi00MC03OC05OC03OGgtMTBjLTYzIDAtOTIgMzUtOTIgNDJIMjM2YzAtNy0yOS00Mi05Mi00MmgtMTV6IiBmaWxsPSIjZmZmIi8+PC9zdmc+)](https://huggingface.co/spaces/WebShepherd/Project-Web-Shepherd)

Web-Shepherd is the **first process reward model (PRM)** designed specifically for web agents. It evaluates trajectories at the step level to provide interpretable and cost-efficient feedback for both learning and inference-time decision making in web navigation tasks.

---

## 🚀 Overview

Recent multimodal language models (MLLMs) have made progress in web automation but struggle with long-horizon planning and cost efficiency. To tackle this, Web-Shepherd introduces:

- **WebPRM Collectionn**: A dataset with 40K+ step-level preference annotations and structured checklists.
- **WebRewardBench**: A benchmark to test PRM effectiveness across diverse web tasks.
- **Web-Shepherd**: A PRM trained to provide step-wise feedback and reward using structured subgoal checklists.

---

## 🧠 Key Features

- ✅ Step-level trajectory evaluation for web agents
- 🧾 Checklist-guided reward modeling for interpretability
- 💰 100× cost reduction compared to prompting GPT-4o
- 📈 Outperforms GPT-4o-mini by **10.9 points** on WebArena-lite
- 🔄 Supports both reward assignment and agent refinement

---

## 💎 Assets

| Resource | Description | Size | Link |
|----------|-------------|------|------|
| WebPRM Collection | Step-level preference annotations with structured checklists | 40K+ annotations | [🤗 huggingface](https://huggingface.co/datasets/LangAGI-Lab/WebPRMCollection_preference_pair) |
| WebRewardBench | Comprehensive benchmark for evaluating PRM effectiveness | 1000+ test cases | [🤗 huggingface](https://huggingface.co/datasets/LangAGI-Lab/WebRewardBench) |
| Web-Shepherd (3B, text-only) | Trained process reward model for web navigation | 350M parameters | [🤗 huggingface](https://huggingface.co/WebShepherd/web-shepherd-base) |
| Web-Shepherd (3B, 🖼️ multimodal) | Trained process reward model for web navigation | 350M parameters | [🤗 huggingface](https://huggingface.co/WebShepherd/web-shepherd-base) |
| Web-Shepherd (8B, text-only) | Enhanced version with improved performance | 1.3B parameters | [🤗 huggingface](https://huggingface.co/WebShepherd/web-shepherd-large) |


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
