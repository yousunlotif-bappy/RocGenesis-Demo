def generate_command_runbook(
    project_name: str,
    framework: str,
    deployment_target: str,
    os_name: str = "Ubuntu 22.04",
    package_manager: str = "pip",
    gpu_target: str = "AMD Instinct MI300X",
):
    """
    Generate a professional AMD/ROCm-ready command runbook.
    This is intentionally deterministic so the app works even without an LLM/API key.
    """

    safe_project_name = (
        project_name.strip()
        .lower()
        .replace(" ", "-")
        .replace("_", "-")
        .replace("/", "-")
    )

    if not safe_project_name:
        safe_project_name = "rocgenesis-project"

    commands = [
        {
            "phase": "Project Setup",
            "step": "Create project directory",
            "command": f"mkdir {safe_project_name} && cd {safe_project_name}",
            "explanation": "Creates a clean project folder and moves into it.",
            "expected_output": f"A new folder named '{safe_project_name}' is created.",
            "amd_note": "Safe local operation. No AMD/ROCm dependency yet.",
            "risk": "Low",
        },
        {
            "phase": "Project Setup",
            "step": "Create virtual environment",
            "command": "python -m venv .venv",
            "explanation": "Creates an isolated Python environment for reproducible development.",
            "expected_output": "A .venv folder is created.",
            "amd_note": "Isolation helps avoid PyTorch/ROCm package conflicts.",
            "risk": "Low",
        },
        {
            "phase": "Environment",
            "step": "Activate virtual environment",
            "command": "source .venv/bin/activate",
            "explanation": "Activates the virtual environment on Linux/macOS. On Windows use .venv\\Scripts\\activate.",
            "expected_output": "Terminal prompt shows the virtual environment is active.",
            "amd_note": "Run all PyTorch/ROCm package commands inside this environment.",
            "risk": "Low",
        },
        {
            "phase": "Environment",
            "step": "Upgrade pip",
            "command": "python -m pip install --upgrade pip",
            "explanation": "Updates pip so dependency installation is more reliable.",
            "expected_output": "pip upgrades successfully.",
            "amd_note": "A recent pip version reduces dependency resolution issues.",
            "risk": "Low",
        },
    ]

    if framework == "Streamlit":
        install_command = "pip install streamlit torch transformers accelerate python-dotenv requests pandas"
        run_command = "streamlit run app.py"
    elif framework == "Gradio":
        install_command = "pip install gradio torch transformers accelerate python-dotenv requests pandas"
        run_command = "python app.py"
    elif framework == "FastAPI":
        install_command = "pip install fastapi uvicorn torch transformers accelerate python-dotenv requests pandas"
        run_command = "uvicorn app:app --reload"
    else:
        install_command = "pip install torch transformers accelerate python-dotenv requests pandas"
        run_command = "python app.py"

    commands.extend(
        [
            {
                "phase": "Dependencies",
                "step": "Install project dependencies",
                "command": install_command,
                "explanation": f"Installs the required packages for a {framework}-based AI application.",
                "expected_output": "All dependencies install without errors.",
                "amd_note": "For actual AMD GPU acceleration, use a ROCm-compatible PyTorch build.",
                "risk": "Low",
            },
            {
                "phase": "Validation",
                "step": "Check PyTorch and ROCm/HIP backend",
                "command": 'python -c "import torch; print(torch.__version__); print(torch.version.hip); print(torch.cuda.is_available())"',
                "explanation": "Checks PyTorch version, ROCm/HIP backend, and AMD GPU availability.",
                "expected_output": "torch.version.hip should show a ROCm/HIP version and GPU availability should be True when ROCm is configured.",
                "amd_note": "PyTorch uses torch.cuda APIs for AMD GPUs through ROCm/HIP.",
                "risk": "Low",
            },
            {
                "phase": "Validation",
                "step": "Check AMD GPU status",
                "command": "rocm-smi",
                "explanation": "Shows AMD GPU status, temperature, VRAM usage, and utilization.",
                "expected_output": "A table showing AMD GPU device information.",
                "amd_note": "Use this before and during model inference to monitor VRAM pressure.",
                "risk": "Low",
            },
            {
                "phase": "Validation",
                "step": "Check ROCm device visibility",
                "command": "rocminfo | grep -i 'Name'",
                "explanation": "Checks whether ROCm can detect AMD GPU devices.",
                "expected_output": "AMD GPU device names appear in the terminal.",
                "amd_note": "If this fails, PyTorch ROCm workloads may not detect the GPU.",
                "risk": "Low",
            },
            {
                "phase": "Run",
                "step": "Run application locally",
                "command": run_command,
                "explanation": f"Starts the {framework} application locally for testing.",
                "expected_output": "Local development server starts successfully.",
                "amd_note": "Test basic app flow before deploying.",
                "risk": "Low",
            },
            {
                "phase": "Test",
                "step": "Monitor GPU while app runs",
                "command": "watch -n 1 rocm-smi",
                "explanation": "Refreshes AMD GPU memory/utilization view every second.",
                "expected_output": "Live GPU usage updates appear in the terminal.",
                "amd_note": "Helpful for detecting memory spikes and OOM risk.",
                "risk": "Low",
            },
        ]
    )

    if deployment_target == "Hugging Face Space":
        commands.extend(
            [
                {
                    "phase": "Deploy",
                    "step": "Prepare Hugging Face Space files",
                    "command": "git add app.py requirements.txt README.md && git commit -m \"Add RocGenesis AMD-ready AI app\"",
                    "explanation": "Stages and commits the required app files.",
                    "expected_output": "A new Git commit is created.",
                    "amd_note": "Keep API keys in Hugging Face Space Secrets, not in code.",
                    "risk": "Low",
                },
                {
                    "phase": "Deploy",
                    "step": "Push project to remote repository",
                    "command": "git push origin main",
                    "explanation": "Pushes project files to the connected GitHub or Hugging Face repository.",
                    "expected_output": "Remote repository receives the latest project files.",
                    "amd_note": "After pushing, verify app launch logs in Hugging Face Space.",
                    "risk": "Low",
                },
            ]
        )
    elif deployment_target == "Docker":
        commands.extend(
            [
                {
                    "phase": "Deploy",
                    "step": "Build Docker image",
                    "command": f"docker build -t {safe_project_name}:latest .",
                    "explanation": "Builds a Docker image for reproducible deployment.",
                    "expected_output": "Docker image builds successfully.",
                    "amd_note": "For AMD GPU containers, validate ROCm runtime support on the host.",
                    "risk": "Medium",
                },
                {
                    "phase": "Deploy",
                    "step": "Run Docker container",
                    "command": f"docker run --rm -p 8501:8501 {safe_project_name}:latest",
                    "explanation": "Runs the containerized application locally.",
                    "expected_output": "Application becomes available on localhost.",
                    "amd_note": "GPU-enabled Docker on ROCm may require additional runtime configuration.",
                    "risk": "Medium",
                },
            ]
        )
    else:
        commands.append(
            {
                "phase": "Deploy",
                "step": "Create local release checklist",
                "command": "python -m pip freeze > requirements.lock.txt",
                "explanation": "Exports exact dependency versions for reproducibility.",
                "expected_output": "requirements.lock.txt is created.",
                "amd_note": "Useful for reproducing the same ROCm/PyTorch environment later.",
                "risk": "Low",
            }
        )

    return commands


def calculate_command_readiness(commands):
    if not commands:
        return {
            "score": 0,
            "level": "Not Ready",
            "estimated_time": "Unknown",
            "estimated_cost": "$0.00",
            "summary": "No commands generated yet.",
        }

    high_risk = sum(1 for item in commands if item.get("risk") == "High")
    medium_risk = sum(1 for item in commands if item.get("risk") == "Medium")

    score = max(30, 98 - high_risk * 25 - medium_risk * 8)

    if score >= 90:
        level = "Excellent"
    elif score >= 75:
        level = "Good"
    elif score >= 55:
        level = "Review Needed"
    else:
        level = "Risky"

    total_commands = len(commands)
    estimated_minutes = max(6, total_commands * 1.5)

    return {
        "score": score,
        "level": level,
        "estimated_time": f"{estimated_minutes:.0f} min",
        "estimated_cost": "$0.27",
        "summary": f"{total_commands} commands generated with {medium_risk} medium-risk item(s) and {high_risk} high-risk item(s).",
    }


def build_command_script(commands):
    lines = []
    lines.append("#!/usr/bin/env bash")
    lines.append("# RocGenesis Command Runbook")
    lines.append("# Generated for AMD-ready AI development")
    lines.append("")

    for item in commands:
        lines.append(f"# Phase: {item.get('phase', 'General')}")
        lines.append(f"# Step: {item.get('step', '')}")
        lines.append(f"# Explanation: {item.get('explanation', '')}")
        lines.append(str(item.get("command", "")))
        lines.append("")

    return "\n".join(lines)


def build_command_report(commands, readiness):
    lines = []
    lines.append("# RocGenesis CommandFlow Report")
    lines.append("")
    lines.append("## Command Readiness")
    lines.append(f"- Score: {readiness.get('score')}/100")
    lines.append(f"- Level: {readiness.get('level')}")
    lines.append(f"- Estimated Setup Time: {readiness.get('estimated_time')}")
    lines.append(f"- Estimated Run Cost: {readiness.get('estimated_cost')}")
    lines.append("")
    lines.append("## Summary")
    lines.append(readiness.get("summary", ""))
    lines.append("")
    lines.append("## Commands")

    for index, item in enumerate(commands, start=1):
        lines.append("")
        lines.append(f"### {index}. {item.get('step')}")
        lines.append(f"**Phase:** {item.get('phase')}")
        lines.append("")
        lines.append("```bash")
        lines.append(str(item.get("command", "")))
        lines.append("```")
        lines.append("")
        lines.append(f"**Explanation:** {item.get('explanation', '')}")
        lines.append("")
        lines.append(f"**Expected Output:** {item.get('expected_output', '')}")
        lines.append("")
        lines.append(f"**AMD/ROCm Note:** {item.get('amd_note', '')}")
        lines.append("")
        lines.append(f"**Risk:** {item.get('risk', 'Low')}")

    return "\n".join(lines)

