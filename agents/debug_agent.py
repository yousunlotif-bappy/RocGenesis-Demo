from utils.llm_client import call_qwen, build_fallback_analysis


def _qwen_debug_analysis(error_log: str, result: dict, use_qwen: bool = True):
    """
    Adds Qwen analysis if available.
    Falls back safely if API key is missing or API fails.
    """

    if not use_qwen:
        return {
            "analysis": "Qwen analysis disabled by user.",
            "mode": "disabled",
            "model": "none",
            "api_ok": False,
        }

    qwen_prompt = f"""
You are RocGenesis DebugFix, an AMD ROCm/PyTorch debugging copilot.

Analyze this developer error:

ERROR LOG:
{error_log}

DETECTED CLASSIFICATION:
Error Type: {result.get("error_type")}
Root Cause: {result.get("root_cause")}
Risk Level: {result.get("risk_level")}
Safety Score: {result.get("safety_score")}/100

FIX STEPS:
{result.get("fix_steps")}

FIXED CODE:
{result.get("fixed_code")}

Give a professional but concise answer with these sections:

1. Deeper Technical Analysis
2. Why this happens on AMD ROCm / HIP / PyTorch
3. Validation Checklist
4. Production Safety Notes
5. Final Recommendation

Do not expose secrets.
Do not suggest dangerous shell commands.
Keep the answer practical for a hackathon demo.
"""

    system_prompt = (
        "You are RocGenesis, an AMD-ready AI development copilot. "
        "You specialize in ROCm, HIP, PyTorch, Transformers, model inference, GPU memory, "
        "safe debugging, and deployment readiness. "
        "Your response must be safe, practical, and concise."
    )

    response = call_qwen(
        prompt=qwen_prompt,
        system_prompt=system_prompt,
        temperature=0.2,
        max_tokens=1300,
    )

    if response["ok"]:
        return {
            "analysis": response["content"],
            "mode": "qwen",
            "model": response["model"],
            "api_ok": True,
        }

    fallback = build_fallback_analysis(
        error_type=result.get("error_type", "Unknown error"),
        root_cause=result.get("root_cause", "Unknown root cause"),
        fix_steps=result.get("fix_steps", []),
    )

    fallback += "\n\n---\n\n"
    fallback += f"**Qwen status:** {response['content']}"

    return {
        "analysis": fallback,
        "mode": "fallback",
        "model": response["model"],
        "api_ok": False,
    }


def analyze_error(error_log: str, use_qwen: bool = True):
    """
    Professional DebugFix analyzer for AMD ROCm/PyTorch/HIP errors.
    Returns a dictionary that matches the app.py UI.
    """

    log = (error_log or "").lower()

    if "hip out of memory" in log or "hiperroroutofmemory" in log or "out of memory" in log:
        result = {
            "error_type": "HIP Out of Memory",
            "root_cause": (
                "The model, batch size, sequence length, precision setting, or runtime overhead "
                "is using more VRAM than the AMD GPU can safely provide."
            ),
            "plain_explanation": (
                "Your AMD GPU memory is full. The workload is too heavy for the current configuration, "
                "so PyTorch/ROCm cannot continue running the model."
            ),
            "risk_level": "Medium-High",
            "safety_score": 88,
            "resolution_confidence": "94%",
            "fix_steps": [
                "Switch from fp32 to bf16 or fp16 precision.",
                "Reduce batch size.",
                "Reduce sequence/context length.",
                "Use torch.inference_mode() for inference.",
                "Use device_map='auto' when loading large models.",
                "Enable low_cpu_mem_usage=True during model loading.",
                "Consider int8/int4 quantization for very large models.",
                "Monitor AMD GPU memory with rocm-smi.",
            ],
            "commands": [
                "rocm-smi",
                "watch -n 1 rocm-smi",
                "python -c \"import torch; print(torch.__version__); print(torch.version.hip); print(torch.cuda.is_available())\"",
            ],
            "fixed_code": """import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "your-model-name"

tokenizer = AutoTokenizer.from_pretrained(model_id)

with torch.inference_mode():
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        low_cpu_mem_usage=True
    )

prompt = "Explain AMD GPUs in simple terms."
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

outputs = model.generate(
    **inputs,
    max_new_tokens=256,
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
    pad_token_id=tokenizer.eos_token_id
)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
""",
            "what_changed": [
                "Changed heavy precision to bfloat16.",
                "Added torch.inference_mode() to reduce memory overhead.",
                "Added device_map='auto' for automatic device placement.",
                "Added low_cpu_mem_usage=True.",
                "Reduced generation pressure with controlled max_new_tokens.",
                "Added pad_token_id for cleaner generation.",
            ],
            "amd_notes": [
                "ROCm memory pressure can appear as HIP out-of-memory errors.",
                "Use rocm-smi to monitor VRAM and GPU utilization.",
                "BF16/FP16 usually improves AMD GPU memory efficiency for inference.",
                "Large models may require MI300X/MI250X class VRAM or quantization.",
            ],
        }

    elif "no hip gpus are available" in log or "cuda.is_available() returned false" in log:
        result = {
            "error_type": "AMD GPU Detection Error",
            "root_cause": (
                "PyTorch cannot detect the AMD GPU through ROCm/HIP. This usually happens when "
                "ROCm, drivers, runtime permissions, or the PyTorch ROCm build are not configured correctly."
            ),
            "plain_explanation": (
                "Your code is running, but PyTorch cannot see the AMD GPU. The system may be using "
                "CPU-only PyTorch or the ROCm environment is not visible."
            ),
            "risk_level": "Medium",
            "safety_score": 92,
            "resolution_confidence": "91%",
            "fix_steps": [
                "Verify ROCm installation.",
                "Check GPU visibility with rocminfo.",
                "Check AMD GPU status with rocm-smi.",
                "Confirm PyTorch has ROCm/HIP support.",
                "Check torch.version.hip.",
                "Restart runtime after installing correct packages.",
                "Use a clean virtual environment.",
            ],
            "commands": [
                "rocminfo | grep -i 'Name'",
                "rocm-smi",
                "python -c \"import torch; print(torch.__version__); print(torch.version.hip); print(torch.cuda.is_available())\"",
            ],
            "fixed_code": """import torch

print("PyTorch version:", torch.__version__)
print("ROCm/HIP version:", torch.version.hip)
print("GPU available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("AMD GPU device:", torch.cuda.get_device_name(0))
else:
    print("ROCm GPU not detected. Check ROCm installation, PyTorch ROCm build, and runtime permissions.")
""",
            "what_changed": [
                "Added explicit ROCm/HIP version check.",
                "Added GPU availability check.",
                "Added AMD GPU device name validation.",
                "Added clear fallback message if GPU is not detected.",
            ],
            "amd_notes": [
                "PyTorch still uses torch.cuda APIs for AMD GPUs through ROCm/HIP.",
                "torch.version.hip should not be None in a working ROCm build.",
                "rocminfo and rocm-smi are useful first-line diagnostics.",
            ],
        }

    elif "torch not compiled with rocm" in log or "rocm support not found" in log:
        result = {
            "error_type": "PyTorch ROCm Build Error",
            "root_cause": (
                "The installed PyTorch package does not include ROCm support. "
                "It may be CPU-only or CUDA-specific."
            ),
            "plain_explanation": (
                "Your PyTorch installation is not compatible with AMD ROCm. "
                "You need a ROCm-enabled PyTorch build."
            ),
            "risk_level": "Medium",
            "safety_score": 93,
            "resolution_confidence": "92%",
            "fix_steps": [
                "Create a clean virtual environment.",
                "Install a ROCm-compatible PyTorch build.",
                "Check Python and ROCm version compatibility.",
                "Verify torch.version.hip after installation.",
                "Avoid mixing CUDA-specific packages with ROCm packages.",
            ],
            "commands": [
                "python -c \"import torch; print(torch.__version__); print(torch.version.hip)\"",
                "pip show torch",
                "rocm-smi",
            ],
            "fixed_code": """import torch

print("PyTorch:", torch.__version__)
print("HIP/ROCm:", torch.version.hip)

if torch.version.hip is None:
    print("This PyTorch build does not appear to include ROCm support.")
else:
    print("ROCm-enabled PyTorch detected.")
""",
            "what_changed": [
                "Added ROCm build validation.",
                "Added check for torch.version.hip.",
                "Added clear message for CPU/CUDA-only PyTorch builds.",
            ],
            "amd_notes": [
                "ROCm-enabled PyTorch is required for AMD GPU acceleration.",
                "Use clean environments to avoid package conflicts.",
                "Always verify torch.version.hip after installation.",
            ],
        }

    elif "rocblas" in log or "rocblas_status" in log:
        result = {
            "error_type": "rocBLAS Runtime Error",
            "root_cause": (
                "The AMD rocBLAS backend encountered a matrix computation or library compatibility issue."
            ),
            "plain_explanation": (
                "The GPU math library used by ROCm had trouble running the operation. "
                "This may be caused by incompatible shapes, dtype, library version mismatch, or memory pressure."
            ),
            "risk_level": "Medium",
            "safety_score": 90,
            "resolution_confidence": "86%",
            "fix_steps": [
                "Check ROCm and PyTorch compatibility.",
                "Try bf16/fp16 instead of unsupported dtype combinations.",
                "Reduce batch size or sequence length.",
                "Update ROCm libraries if needed.",
                "Verify model tensor shapes.",
                "Run a minimal PyTorch ROCm matrix multiplication test.",
            ],
            "commands": [
                "rocm-smi",
                "python -c \"import torch; x=torch.randn(1024,1024,device='cuda'); print((x@x).shape)\"",
            ],
            "fixed_code": """import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

x = torch.randn(1024, 1024, device=device, dtype=torch.float16)
y = torch.matmul(x, x)

print("rocBLAS test output shape:", y.shape)
""",
            "what_changed": [
                "Added minimal rocBLAS matrix multiplication test.",
                "Used fp16 tensor for GPU-friendly operation.",
                "Added device fallback validation.",
            ],
            "amd_notes": [
                "rocBLAS is AMD's GPU math library for linear algebra.",
                "Many model operations depend on rocBLAS internally.",
                "Minimal matmul tests help isolate environment issues.",
            ],
        }

    elif "miopen" in log:
        result = {
            "error_type": "MIOpen Runtime Error",
            "root_cause": (
                "The AMD MIOpen backend encountered an issue, often related to deep learning kernels, "
                "convolution operations, cache, or compatibility."
            ),
            "plain_explanation": (
                "The AMD deep learning library had trouble running a neural network operation."
            ),
            "risk_level": "Medium",
            "safety_score": 90,
            "resolution_confidence": "84%",
            "fix_steps": [
                "Check ROCm and MIOpen installation.",
                "Clear MIOpen cache if needed.",
                "Verify input tensor shapes.",
                "Reduce batch size.",
                "Try a stable PyTorch ROCm version.",
            ],
            "commands": [
                "rocm-smi",
                "python -c \"import torch; print(torch.version.hip); print(torch.cuda.is_available())\"",
            ],
            "fixed_code": """import torch

print("GPU available:", torch.cuda.is_available())
print("HIP version:", torch.version.hip)

# If MIOpen error continues:
# 1. Reduce batch size
# 2. Verify input tensor shape
# 3. Try a stable ROCm/PyTorch version
""",
            "what_changed": [
                "Added environment checks.",
                "Recommended batch size reduction.",
                "Added tensor shape validation reminder.",
            ],
            "amd_notes": [
                "MIOpen is AMD's deep learning primitives library.",
                "Vision models and convolution-heavy workloads may trigger MIOpen.",
            ],
        }

    elif "device-side assert" in log:
        result = {
            "error_type": "Device-side Assert",
            "root_cause": (
                "A GPU kernel assertion failed. Common causes include invalid labels, shape mismatch, "
                "token index errors, or unsupported operation inputs."
            ),
            "plain_explanation": (
                "The GPU found invalid data during execution. This is often not a hardware problem; "
                "it usually means the model received incorrect labels, shapes, or indexes."
            ),
            "risk_level": "Medium",
            "safety_score": 89,
            "resolution_confidence": "82%",
            "fix_steps": [
                "Run the same code on CPU to get a clearer error.",
                "Check label ranges and tensor shapes.",
                "Validate tokenizer vocabulary size and token IDs.",
                "Restart runtime after a device-side assert.",
                "Use smaller test inputs to isolate the failing sample.",
            ],
            "commands": [
                "python -c \"import torch; print(torch.__version__); print(torch.version.hip)\"",
                "rocm-smi",
            ],
            "fixed_code": """# Debug strategy:
# Run a small batch first and validate tensor shapes/ranges before GPU execution.

def validate_batch(input_ids, labels=None, vocab_size=None):
    print("input_ids shape:", input_ids.shape)

    if vocab_size is not None:
        assert input_ids.max().item() < vocab_size, "Token id exceeds vocabulary size"

    if labels is not None:
        print("labels shape:", labels.shape)
        assert labels.min().item() >= -100, "Invalid label value detected"

    return True
""",
            "what_changed": [
                "Added batch validation helper.",
                "Added token ID and label range checks.",
                "Recommended CPU-first debugging.",
            ],
            "amd_notes": [
                "After a device-side assert, restart the runtime before re-testing.",
                "Small batch validation reduces GPU debugging time.",
            ],
        }

    else:
        result = {
            "error_type": "Unknown ROCm/PyTorch Issue",
            "root_cause": "RocGenesis could not match this error to a known pattern yet.",
            "plain_explanation": (
                "The error may be related to dependencies, model loading, device mapping, memory, "
                "framework configuration, unsupported operations, or runtime compatibility."
            ),
            "risk_level": "Unknown",
            "safety_score": 80,
            "resolution_confidence": "70%",
            "fix_steps": [
                "Check the full stack trace.",
                "Verify Python, PyTorch, ROCm, and GPU compatibility.",
                "Run basic ROCm and PyTorch diagnostic commands.",
                "Reduce model size, batch size, or sequence length if memory is involved.",
                "Check whether all dependencies are installed.",
                "Use a clean virtual environment.",
            ],
            "commands": [
                "rocm-smi",
                "rocminfo | grep -i 'Name'",
                "python -c \"import torch; print(torch.__version__); print(torch.version.hip); print(torch.cuda.is_available())\"",
                "pip freeze",
            ],
            "fixed_code": "# Paste a more specific error log for a targeted fix.",
            "what_changed": [
                "Generated general ROCm/PyTorch diagnostic workflow.",
                "Added compatibility validation steps.",
                "Added fallback debugging commands.",
            ],
            "amd_notes": [
                "Start with rocm-smi, rocminfo, and torch.version.hip.",
                "If memory is involved, reduce model size or precision.",
                "If GPU is not detected, check ROCm runtime and PyTorch build.",
            ],
        }

    qwen = _qwen_debug_analysis(error_log, result, use_qwen=use_qwen)

    result["qwen_analysis"] = qwen["analysis"]
    result["qwen_mode"] = qwen["mode"]
    result["qwen_model"] = qwen["model"]
    result["qwen_api_ok"] = qwen["api_ok"]

    return result

