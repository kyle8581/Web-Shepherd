# 🐑 WEB-SHEPHERD: Process Reward Modeling for Web Agents

**WEB-SHEPHERD** is the first dedicated **Process Reward Model (PRM)** for web agents, enabling fine-grained, step-level evaluation of web navigation trajectories. This project includes:

- **WEBPRM COLLECTION**: A large-scale dataset of 40K step-level annotations with expert and rejected actions across diverse web tasks.
- **WEBREWARDBENCH**: The first benchmark for evaluating PRMs on web navigation.
- **WEB-SHEPHERD Model**: A reward model trained to evaluate step-level progress using structured checklists.

[[📚 Paper (NeurIPS 2025 submission)](https://hf.co/spaces/WebShepherd/Project-Web-Shepherd)]

## 🚀 Highlights

- **Cost-efficient**: 10× cheaper than GPT-4o-mini while achieving better performance.
- **Structured reward modeling**: Checklist-based process evaluation enables dense, interpretable feedback.
- **Generalizable**: Applicable across domains (shopping, travel, CMS, etc.) and difficulty levels (easy to hard).
- **Improves web agent performance**: Boosts GPT-4o-mini's WebArena-lite success rate by +10.9 points.

## 🧱 Components

### 1. WEBPRM COLLECTION
A dataset of:
- Human-written instructions
- Expert and rejected trajectories
- Structured checklists (subgoals)
- Annotated rewards per step

### 2. WEBREWARDBENCH
Evaluation suite with:
- Preference-labeled action pairs
- Metrics: MRR (step), Accuracy (step/traj)
- Cross-domain and cross-task generalization

### 3. WEB-SHEPHERD Model
- Text-only and multimodal variants (Qwen2.5-3B, 8B, VL-3B)
- Trained via next-token prediction with verbalized reward outputs
- LoRA + LLaMA-Factory compatible training pipeline

## 📦 Installation

```bash
git clone https://github.com/<your-org>/web-shepherd.git
cd web-shepherd
conda env create -f environment.yml
conda activate webshepherd
