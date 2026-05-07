GPU_PROFILES = {
    "AMD Instinct MI300X": {
        "vram_gb": 192,
        "class": "Datacenter",
        "best_for": "70B inference, fine-tuning, multimodal workloads",
        "relative_speed": 1.0,
        "estimated_cost_per_hour": 5.0,
    },
    "AMD Instinct MI250X": {
        "vram_gb": 128,
        "class": "Datacenter",
        "best_for": "13B/34B inference, medium fine-tuning",
        "relative_speed": 0.72,
        "estimated_cost_per_hour": 3.5,
    },
    "AMD Radeon AI PRO R9700": {
        "vram_gb": 32,
        "class": "Workstation",
        "best_for": "7B/13B prototype inference, local AI development",
        "relative_speed": 0.38,
        "estimated_cost_per_hour": 1.2,
    },
    "AMD Radeon RX 7900 XTX": {
        "vram_gb": 24,
        "class": "Consumer",
        "best_for": "Small model inference, local testing",
        "relative_speed": 0.30,
        "estimated_cost_per_hour": 0.8,
    },
}


PRECISION_BYTES = {
    "fp32": 4,
    "fp16": 2,
    "bf16": 2,
    "int8": 1,
    "int4": 0.5,
}


def estimate_vram(
    model_size_b: float,
    precision: str,
    batch_size: int,
    sequence_length: int,
    task_type: str,
):
    """
    Practical VRAM estimator for LLM-style workloads.
    This is an approximation for planning, not a hardware benchmark.
    """

    precision = precision.lower()
    if precision not in PRECISION_BYTES:
        precision = "fp16"

    batch_size = max(int(batch_size), 1)
    sequence_length = max(int(sequence_length), 512)
    model_size_b = float(model_size_b)

    bytes_per_param = PRECISION_BYTES[precision]

    # Weight memory: B params * bytes per param
    base_memory_gb = model_size_b * bytes_per_param

    # KV cache estimate. Larger sequence + batch increases cache pressure.
    seq_factor = sequence_length / 4096
    kv_cache_gb = model_size_b * 0.28 * seq_factor * batch_size

    # Activation/runtime overhead depends on workload type.
    task_type = task_type.lower()

    if task_type == "fine-tuning":
        overhead_ratio = 0.85
    elif task_type == "serving":
        overhead_ratio = 0.42
    else:
        overhead_ratio = 0.25

    runtime_overhead_gb = base_memory_gb * overhead_ratio

    # Embeddings, tokenizer buffers, framework overhead, fragmentation.
    framework_overhead_gb = max(1.2, model_size_b * 0.08)

    total_memory_gb = (
        base_memory_gb
        + kv_cache_gb
        + runtime_overhead_gb
        + framework_overhead_gb
    )

    return {
        "model_size_b": model_size_b,
        "precision": precision,
        "batch_size": batch_size,
        "sequence_length": sequence_length,
        "task_type": task_type.title(),
        "base_memory_gb": round(base_memory_gb, 2),
        "kv_cache_gb": round(kv_cache_gb, 2),
        "overhead_gb": round(runtime_overhead_gb, 2),
        "framework_overhead_gb": round(framework_overhead_gb, 2),
        "total_memory_gb": round(total_memory_gb, 2),
    }


def get_gpu_recommendation(total_memory_gb: float, gpu_vram_gb: float):
    utilization = (total_memory_gb / gpu_vram_gb) * 100

    if utilization <= 65:
        risk = "Low"
        status = "Good Fit"
        readiness = "Ready"
        fit_score = 95
        advice = "This workload should fit comfortably on the selected AMD GPU."
    elif utilization <= 85:
        risk = "Medium"
        status = "Usable"
        readiness = "Review Recommended"
        fit_score = 82
        advice = "This workload may run, but there is moderate memory pressure. Reduce batch size or sequence length for safer execution."
    elif utilization <= 100:
        risk = "High"
        status = "Tight Fit"
        readiness = "High Caution"
        fit_score = 64
        advice = "This workload is close to the VRAM limit. Use optimization before running."
    else:
        risk = "Critical"
        status = "Not Recommended"
        readiness = "Not Ready"
        fit_score = 35
        advice = "This workload likely exceeds available VRAM. Use a larger AMD GPU or stronger optimization."

    return {
        "utilization": round(utilization, 1),
        "risk": risk,
        "status": status,
        "readiness": readiness,
        "fit_score": fit_score,
        "advice": advice,
    }


def optimization_tips(precision: str, task_type: str, total_memory_gb: float = None, gpu_vram_gb: float = None):
    precision = precision.lower()
    task_type = task_type.lower()

    tips = []

    if precision == "fp32":
        tips.append({
            "title": "Switch FP32 to BF16/FP16",
            "impact": "High",
            "detail": "FP32 uses 4 bytes per parameter. BF16/FP16 cuts model weight memory roughly in half.",
        })

    if precision in ["fp16", "bf16"]:
        tips.append({
            "title": "Keep mixed precision enabled",
            "impact": "Medium",
            "detail": "BF16/FP16 is usually a strong choice for AMD GPU inference and serving workloads.",
        })

    if precision not in ["int8", "int4"]:
        tips.append({
            "title": "Consider INT8/INT4 quantization",
            "impact": "High",
            "detail": "Quantization can significantly reduce VRAM usage for large models.",
        })

    tips.append({
        "title": "Reduce batch size",
        "impact": "High",
        "detail": "Batch size directly increases activation and KV-cache memory pressure.",
    })

    tips.append({
        "title": "Reduce sequence length",
        "impact": "Medium",
        "detail": "Long context windows increase KV-cache memory usage.",
    })

    tips.append({
        "title": "Use device_map='auto'",
        "impact": "Medium",
        "detail": "Automatic device mapping helps distribute large models across available devices.",
    })

    tips.append({
        "title": "Use torch.inference_mode()",
        "impact": "Medium",
        "detail": "Inference mode disables gradient tracking and reduces runtime memory overhead.",
    })

    if task_type == "fine-tuning":
        tips.append({
            "title": "Use gradient checkpointing",
            "impact": "High",
            "detail": "Gradient checkpointing reduces activation memory during fine-tuning.",
        })
        tips.append({
            "title": "Prefer LoRA/QLoRA",
            "impact": "High",
            "detail": "Parameter-efficient fine-tuning is more practical than full fine-tuning for large models.",
        })

    if task_type in ["serving", "inference"]:
        tips.append({
            "title": "Enable Flash Attention if supported",
            "impact": "Medium",
            "detail": "Flash Attention can reduce memory pressure and improve throughput.",
        })

    if total_memory_gb and gpu_vram_gb and total_memory_gb > gpu_vram_gb:
        tips.insert(0, {
            "title": "Use a larger AMD GPU",
            "impact": "Critical",
            "detail": "The estimated memory exceeds the selected GPU VRAM. Choose MI300X/MI250X or reduce workload size.",
        })

    return tips


def estimate_optimized_vram(result: dict):
    """
    Estimate after applying common optimizations:
    - lower precision if fp32
    - reduced batch pressure
    - reduced overhead from inference mode / optimized attention
    """

    before = result["total_memory_gb"]
    precision = result["precision"]
    task_type = result["task_type"].lower()

    reduction = 0.0

    if precision == "fp32":
        reduction += 0.32

    if task_type == "fine-tuning":
        reduction += 0.18
    elif task_type == "serving":
        reduction += 0.12
    else:
        reduction += 0.10

    reduction += 0.07  # general runtime cleanup

    reduction = min(reduction, 0.45)
    after = before * (1 - reduction)

    return {
        "before_gb": round(before, 2),
        "after_gb": round(after, 2),
        "reduction_percent": round(reduction * 100, 1),
        "saved_gb": round(before - after, 2),
    }


def compare_gpus(total_memory_gb: float, task_type: str):
    rows = []

    for name, profile in GPU_PROFILES.items():
        vram = profile["vram_gb"]
        rec = get_gpu_recommendation(total_memory_gb, vram)

        if rec["risk"] in ["Low", "Medium"]:
            recommendation = "Recommended" if name == "AMD Instinct MI300X" else "Usable"
        elif rec["risk"] == "High":
            recommendation = "Caution"
        else:
            recommendation = "Not Recommended"

        # Simple relative runtime estimate. Not a benchmark.
        runtime_minutes = max(1.5, (total_memory_gb / 50) / profile["relative_speed"] * 3)
        cost_per_run = (runtime_minutes / 60) * profile["estimated_cost_per_hour"]

        rows.append({
            "GPU": name,
            "Class": profile["class"],
            "VRAM (GB)": vram,
            "Utilization": f"{rec['utilization']}%",
            "Fit Status": rec["status"],
            "OOM Risk": rec["risk"],
            "Est. Runtime": f"{runtime_minutes:.1f} min",
            "Est. Cost": f"${cost_per_run:.2f}",
            "Recommendation": recommendation,
        })

    return rows


def build_gpu_report(result, recommendation, comparison_rows, tips, optimized):
    lines = []

    lines.append("# RocGenesis GPU Estimate Report")
    lines.append("")
    lines.append("## Model Configuration")
    lines.append(f"- Model Size: {result['model_size_b']}B parameters")
    lines.append(f"- Precision: {result['precision']}")
    lines.append(f"- Batch Size: {result['batch_size']}")
    lines.append(f"- Sequence Length: {result['sequence_length']}")
    lines.append(f"- Task Type: {result['task_type']}")
    lines.append("")

    lines.append("## Estimated VRAM Usage")
    lines.append(f"- Base Model Memory: {result['base_memory_gb']} GB")
    lines.append(f"- KV Cache Estimate: {result['kv_cache_gb']} GB")
    lines.append(f"- Runtime Overhead: {result['overhead_gb']} GB")
    lines.append(f"- Framework Overhead: {result['framework_overhead_gb']} GB")
    lines.append(f"- Total Estimated VRAM: {result['total_memory_gb']} GB")
    lines.append("")

    lines.append("## Selected GPU Recommendation")
    lines.append(f"- Utilization: {recommendation['utilization']}%")
    lines.append(f"- Fit Status: {recommendation['status']}")
    lines.append(f"- OOM Risk: {recommendation['risk']}")
    lines.append(f"- Fit Score: {recommendation['fit_score']}/100")
    lines.append(f"- Readiness: {recommendation['readiness']}")
    lines.append(f"- Advice: {recommendation['advice']}")
    lines.append("")

    lines.append("## Before vs After Optimization")
    lines.append(f"- Before: {optimized['before_gb']} GB")
    lines.append(f"- After: {optimized['after_gb']} GB")
    lines.append(f"- Estimated Reduction: {optimized['reduction_percent']}%")
    lines.append(f"- Estimated VRAM Saved: {optimized['saved_gb']} GB")
    lines.append("")

    lines.append("## AMD GPU Comparison")
    for row in comparison_rows:
        lines.append(
            f"- {row['GPU']} | VRAM: {row['VRAM (GB)']} GB | "
            f"Utilization: {row['Utilization']} | Risk: {row['OOM Risk']} | "
            f"Recommendation: {row['Recommendation']}"
        )

    lines.append("")
    lines.append("## Optimization Suggestions")
    for tip in tips:
        lines.append(f"- [{tip['impact']}] {tip['title']}: {tip['detail']}")

    lines.append("")
    lines.append("## Note")
    lines.append("This is an estimate for planning. Actual VRAM usage may vary based on model implementation, tokenizer, runtime, kernels, framework version, and ROCm/PyTorch compatibility.")

    return "\n".join(lines)

