# SLM Eval Quickstart

Run your first AI evaluation in 5 minutes.

## What this is

A minimal, runnable evaluation pipeline for SLMs and prompt quality. It uses `promptfoo` to run a simple test case against a local or mock provider.

## Prerequisites

- Python 3.11+
- Git
- Docker (optional, only if you want to run a local model container)

## Setup

```bash
git clone https://github.com/bmrtech-oss/ai-development-playbook.git
cd ai-development-playbook/quickstart/slm-eval-template
python -m venv .venv
.venv/Scripts/activate  # Windows
# or
source .venv/bin/activate  # macOS/Linux
pip install -U pip
pip install -r requirements.txt
```

## Run the sample evaluation

```bash
python src/eval.py
```

If you want to run against a local provider or mock model, update `promptfooconfig.yaml` with the provider endpoint of your choice.

## What you should see

- A `promptfoo` evaluation run
- A pass/fail summary for a single prompt case
- Minimal setup required for your first SLM evaluation

## Learn more

For full playbook context and advanced workflows, see the main repository: [`README.md`](../README.md)
