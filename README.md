---
title: RocGenesis
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.40.1
app_file: app.py
pinned: false
license: mit
short_description: AMD-ready AI Development Copilot for AI builders
---

# RocGenesis — AMD-ready AI Development Copilot

**RocGenesis** is an AI-powered development copilot that helps developers design, debug, secure, optimize, and prepare AMD GPU-ready AI applications for deployment.

It combines project blueprinting, safe command generation, ROCm/PyTorch debugging, GPU workload estimation, safety scanning, and final report generation in one guided dashboard.

---

Live Demo
https://rocgenesis-demo.onrender.com/

https://huggingface.co/spaces/yousunlotif/RocGenesis

## 🚀 Tagline

**Build, debug, secure, optimize, and ship AI apps on AMD GPUs.**

---

## 📌 Problem Statement

Building GPU-powered AI applications is powerful, but developers often face several problems:

- ROCm and AMD GPU setup can be confusing.
- PyTorch, HIP, and ROCm errors are difficult to understand.
- GPU memory usage and out-of-memory risk are hard to estimate before running a model.
- Safe terminal commands and deployment steps are often scattered.
- Risky code, unsafe commands, secrets, and unsafe model loading patterns may be missed.
- Preparing final documentation and reports takes extra time.

RocGenesis solves these problems by bringing the full AMD-ready AI development workflow into one guided dashboard.

---

## ✅ Solution Overview

RocGenesis helps developers move from raw idea to AMD-ready deployment through a complete workflow:

1. **Design & Build Flow**  
   Converts a raw AI project idea into an AMD-ready project blueprint.

2. **CommandFlow**  
   Generates safe setup, validation, run, test, and deployment commands.

3. **DebugFix**  
   Analyzes ROCm, HIP, and PyTorch errors with root cause, fixed code, and test commands.

4. **Safety Guard**  
   Scans code, commands, secrets, dependencies, and unsafe patterns.

5. **GPU Estimate**  
   Estimates VRAM usage, OOM risk, AMD GPU fit, and optimization strategy.

6. **Reports**  
   Generates final judge-ready project reports and deployment evidence.

---

## 🎯 Key Features

### AI Project Blueprinting

- Converts raw project ideas into structured plans.
- Suggests project architecture and file structure.
- Recommends AMD/ROCm-aware development steps.
- Helps prepare a project for deployment.

### CommandFlow

- Generates professional terminal command runbooks.
- Explains what each command does.
- Shows expected output.
- Adds AMD/ROCm notes.
- Performs command safety review.

### DebugFix

- Detects common ROCm, HIP, and PyTorch error types.
- Explains root cause in simple language.
- Suggests ROCm-friendly fixed code.
- Provides validation and test commands.
- Supports Qwen-powered deeper reasoning.

### Safety Guard

- Detects risky shell commands.
- Detects hardcoded API keys and secrets.
- Flags unsafe model loading patterns.
- Checks dependency and deployment safety.
- Produces safety score and safe recommendations.

### GPU Estimate

- Estimates model memory requirements.
- Predicts out-of-memory risk.
- Calculates AMD GPU fit.
- Suggests optimization strategies such as BF16/FP16, batching, sequence length reduction, and memory optimization.

### Reports

- Generates final project documentation.
- Includes blueprint, commands, debug analysis, safety results, GPU estimate, and deployment readiness.
- Helps prepare hackathon submission, GitHub README, and demo explanation.

---

## 🧠 Why RocGenesis Stands Out

RocGenesis is not only a UI dashboard. It is a guided AI developer workflow for AMD GPU application development.

### AMD-ready by Design

RocGenesis focuses on AMD GPU workflows, ROCm setup, PyTorch ROCm checks, HIP/ROCm debugging, and AMD deployment guidance.

### Agentic Developer Workflow

It connects planning, command generation, debugging, safety review, GPU estimation, and reporting into one guided lifecycle.

### Submission-ready Output

It produces command runbooks, safety notes, GPU reports, DebugFix explanations, and final project documentation that can be used for hackathon or production review.

---

## 🧩 Application Modules

| Module | Purpose |
|---|---|
| Dashboard | Central project overview, quick actions, and workflow summary |
| Design & Build Flow | Generate AMD-ready project blueprint |
| CommandFlow | Generate safe commands and command runbooks |
| DebugFix | Analyze ROCm/PyTorch/HIP errors |
| Safety Guard | Scan code, commands, secrets, and risky patterns |
| GPU Estimate | Estimate VRAM, OOM risk, and AMD GPU fit |
| Reports | Generate final project report |
| Settings | View API, model, and safety configuration |

---

## 🛠️ Tech Stack

- **App Framework:** Streamlit
- **Programming Language:** Python
- **AI Model Integration:** Qwen through OpenRouter API
- **Target Runtime:** PyTorch + ROCm
- **GPU Focus:** AMD GPUs
- **Report Format:** Markdown
- **Deployment Target:** Hugging Face Spaces

---

## ⚙️ Project Structure

```text
RocGenesis/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── agents/
│   ├── __init__.py
│   ├── design_agent.py
│   ├── command_agent.py
│   ├── debug_agent.py
│   ├── gpu_estimator.py
│   ├── report_agent.py
│   └── safety_agent.py
│
├── utils/
│   ├── __init__.py
│   ├── llm_client.py
│   ├── report_builder.py
│   └── safety_rules.py
│
├── data/
│   ├── command_templates.json
│   ├── gpu_profiles.json
│   └── rocm_errors.json
│
└── assets/
    └── logo_clean.png


    
