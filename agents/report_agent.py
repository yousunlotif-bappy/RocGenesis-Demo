def calculate_report_scores(
    blueprint=None,
    commands=None,
    debug_result=None,
    gpu_result=None,
    safety_result=None,
):
    completed = 0
    total = 5

    if blueprint:
        completed += 1
    if commands:
        completed += 1
    if debug_result:
        completed += 1
    if gpu_result:
        completed += 1
    if safety_result:
        completed += 1

    completeness = int((completed / total) * 100)

    safety_score = 92
    if safety_result:
        safety_score = int(safety_result.get("score", 92))
    elif debug_result:
        safety_score = int(debug_result.get("safety_score", 88))

    amd_readiness = 70
    if gpu_result:
        amd_readiness += 20
    if commands:
        amd_readiness += 5
    if blueprint:
        amd_readiness += 5
    amd_readiness = min(100, amd_readiness)

    export_readiness = 70
    if completeness >= 80:
        export_readiness = 95
    elif completeness >= 60:
        export_readiness = 85
    elif completeness >= 40:
        export_readiness = 75

    deployment_readiness = int((completeness * 0.35) + (safety_score * 0.30) + (amd_readiness * 0.35))

    if deployment_readiness >= 90:
        readiness_label = "Ready for Submission"
    elif deployment_readiness >= 75:
        readiness_label = "Almost Ready"
    elif deployment_readiness >= 60:
        readiness_label = "Needs Review"
    else:
        readiness_label = "Incomplete"

    return {
        "completeness": completeness,
        "safety_score": safety_score,
        "amd_readiness": amd_readiness,
        "export_readiness": export_readiness,
        "deployment_readiness": deployment_readiness,
        "readiness_label": readiness_label,
        "completed_sections": completed,
        "total_sections": total,
    }


def build_full_project_report(
    project_name: str,
    blueprint=None,
    commands=None,
    command_readiness=None,
    debug_result=None,
    gpu_result=None,
    gpu_recommendation=None,
    gpu_optimized=None,
    gpu_comparison=None,
    safety_result=None,
):
    scores = calculate_report_scores(
        blueprint=blueprint,
        commands=commands,
        debug_result=debug_result,
        gpu_result=gpu_result,
        safety_result=safety_result,
    )

    lines = []

    lines.append(f"# {project_name} — RocGenesis Final Project Report")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append(
        "RocGenesis is an AMD-ready AI development copilot designed to help developers turn AI project ideas into deployment-ready AMD GPU applications. "
        "It supports project planning, safe command generation, ROCm/PyTorch debugging, safety scanning, GPU memory estimation, optimization guidance, and final reporting."
    )
    lines.append("")

    lines.append("## Report Scores")
    lines.append(f"- Report Completeness: {scores['completeness']}/100")
    lines.append(f"- Safety Score: {scores['safety_score']}/100")
    lines.append(f"- AMD Readiness: {scores['amd_readiness']}/100")
    lines.append(f"- Export Readiness: {scores['export_readiness']}/100")
    lines.append(f"- Deployment Readiness: {scores['deployment_readiness']}/100")
    lines.append(f"- Final Status: {scores['readiness_label']}")
    lines.append("")

    lines.append("## Project Overview")
    if blueprint:
        lines.append(f"**Summary:** {blueprint.get('summary', 'No summary available.')}")
        lines.append("")
        lines.append("### Target Users")
        lines.append(str(blueprint.get("target_users", "Not specified")))
        lines.append("")
        lines.append("### Core Features")
        for item in blueprint.get("core_features", []):
            lines.append(f"- {item}")
        lines.append("")
        lines.append("### Architecture")
        for item in blueprint.get("architecture", []):
            lines.append(f"- {item}")
        lines.append("")
        lines.append("### Recommended Tech Stack")
        for item in blueprint.get("tech_stack", []):
            lines.append(f"- {item}")
        lines.append("")
        lines.append("### AMD / ROCm Notes")
        for item in blueprint.get("amd_notes", []):
            lines.append(f"- {item}")
    else:
        lines.append("No blueprint generated yet.")
    lines.append("")

    lines.append("## CommandFlow Summary")
    if commands:
        if command_readiness:
            lines.append(f"- Command Readiness: {command_readiness.get('score')}/100")
            lines.append(f"- Level: {command_readiness.get('level')}")
            lines.append(f"- Estimated Setup Time: {command_readiness.get('estimated_time')}")
            lines.append(f"- Estimated Run Cost: {command_readiness.get('estimated_cost')}")
            lines.append(f"- Summary: {command_readiness.get('summary')}")
            lines.append("")

        for idx, item in enumerate(commands, start=1):
            lines.append(f"### {idx}. {item.get('step', 'Command Step')}")
            lines.append(f"**Phase:** {item.get('phase', 'General')}")
            lines.append("")
            lines.append("```bash")
            lines.append(str(item.get("command", "")))
            lines.append("```")
            lines.append("")
            lines.append(f"**Explanation:** {item.get('explanation', '')}")
            lines.append(f"**Expected Output:** {item.get('expected_output', '')}")
            lines.append(f"**AMD/ROCm Note:** {item.get('amd_note', '')}")
            lines.append(f"**Risk:** {item.get('risk', 'Low')}")
            lines.append("")
    else:
        lines.append("No CommandFlow runbook generated yet.")
    lines.append("")

    lines.append("## DebugFix Summary")
    if debug_result:
        lines.append(f"- Error Type: {debug_result.get('error_type', 'Unknown')}")
        lines.append(f"- Risk Level: {debug_result.get('risk_level', 'Unknown')}")
        lines.append(f"- Safety Score: {debug_result.get('safety_score', 80)}/100")
        lines.append(f"- Resolution Confidence: {debug_result.get('resolution_confidence', '70%')}")
        lines.append("")
        lines.append("### Root Cause")
        lines.append(str(debug_result.get("root_cause", "No root cause available.")))
        lines.append("")
        lines.append("### Plain-language Explanation")
        lines.append(str(debug_result.get("plain_explanation", "No explanation available.")))
        lines.append("")
        lines.append("### Fix Steps")
        for step in debug_result.get("fix_steps", []):
            lines.append(f"- {step}")
        lines.append("")
        lines.append("### Test Commands")
        for cmd in debug_result.get("commands", []):
            lines.append("```bash")
            lines.append(str(cmd))
            lines.append("```")
        lines.append("")
        lines.append("### Fixed Code")
        lines.append("```python")
        lines.append(str(debug_result.get("fixed_code", "# No fixed code available.")))
        lines.append("```")
    else:
        lines.append("No DebugFix analysis generated yet.")
    lines.append("")

    lines.append("## Safety Guard Summary")
    if safety_result:
        lines.append(f"- Safety Score: {safety_result.get('score')}/100")
        lines.append(f"- Risk Level: {safety_result.get('risk_level')}")
        lines.append(f"- Summary: {safety_result.get('summary')}")
        lines.append("")
        issues = safety_result.get("issues", [])
        if issues:
            lines.append("### Issues Detected")
            for issue in issues:
                lines.append(f"- Pattern: `{issue.get('pattern')}`")
                lines.append(f"  - Risk: {issue.get('risk')}")
                lines.append(f"  - Reason: {issue.get('reason')}")
                lines.append(f"  - Safe Fix: {issue.get('safe_fix')}")
        else:
            lines.append("No critical safety issues detected.")
    else:
        lines.append("No Safety Guard scan generated yet.")
    lines.append("")

    lines.append("## GPU Estimate Summary")
    if gpu_result:
        lines.append("### Model Configuration")
        lines.append(f"- Model Size: {gpu_result.get('model_size_b')}B parameters")
        lines.append(f"- Precision: {gpu_result.get('precision')}")
        lines.append(f"- Batch Size: {gpu_result.get('batch_size')}")
        lines.append(f"- Sequence Length: {gpu_result.get('sequence_length')}")
        lines.append(f"- Task Type: {gpu_result.get('task_type')}")
        lines.append("")
        lines.append("### VRAM Estimate")
        lines.append(f"- Base Model Memory: {gpu_result.get('base_memory_gb')} GB")
        lines.append(f"- KV Cache: {gpu_result.get('kv_cache_gb')} GB")
        lines.append(f"- Runtime Overhead: {gpu_result.get('overhead_gb')} GB")
        lines.append(f"- Framework Overhead: {gpu_result.get('framework_overhead_gb')} GB")
        lines.append(f"- Total Estimated VRAM: {gpu_result.get('total_memory_gb')} GB")
        lines.append("")

        if gpu_recommendation:
            lines.append("### Selected GPU Recommendation")
            lines.append(f"- Utilization: {gpu_recommendation.get('utilization')}%")
            lines.append(f"- Fit Status: {gpu_recommendation.get('status')}")
            lines.append(f"- OOM Risk: {gpu_recommendation.get('risk')}")
            lines.append(f"- Fit Score: {gpu_recommendation.get('fit_score')}/100")
            lines.append(f"- Readiness: {gpu_recommendation.get('readiness')}")
            lines.append(f"- Advice: {gpu_recommendation.get('advice')}")
            lines.append("")

        if gpu_optimized:
            lines.append("### Before vs After Optimization")
            lines.append(f"- Before: {gpu_optimized.get('before_gb')} GB")
            lines.append(f"- After: {gpu_optimized.get('after_gb')} GB")
            lines.append(f"- Reduction: {gpu_optimized.get('reduction_percent')}%")
            lines.append(f"- Saved VRAM: {gpu_optimized.get('saved_gb')} GB")
            lines.append("")

        if gpu_comparison:
            lines.append("### AMD GPU Comparison")
            for row in gpu_comparison:
                lines.append(
                    f"- {row.get('GPU')} | VRAM: {row.get('VRAM (GB)')} GB | "
                    f"Utilization: {row.get('Utilization')} | Risk: {row.get('OOM Risk')} | "
                    f"Recommendation: {row.get('Recommendation')}"
                )
    else:
        lines.append("No GPU Estimate generated yet.")
    lines.append("")

    lines.append("## Deployment Checklist")
    lines.append("- [ ] Project idea and architecture reviewed")
    lines.append("- [ ] Commands generated and safety checked")
    lines.append("- [ ] ROCm/PyTorch environment validation planned")
    lines.append("- [ ] DebugFix tested with at least one real ROCm/PyTorch error")
    lines.append("- [ ] GPU memory estimate generated")
    lines.append("- [ ] Safety Guard scan completed")
    lines.append("- [ ] README prepared")
    lines.append("- [ ] Hugging Face Space or public demo link prepared")
    lines.append("- [ ] Demo video prepared")
    lines.append("- [ ] Final project report exported")
    lines.append("")

    lines.append("## Final Recommendation")
    if scores["deployment_readiness"] >= 90:
        lines.append("This project is ready for final hackathon submission. Focus next on demo video, README, screenshots, and clear public presentation.")
    elif scores["deployment_readiness"] >= 75:
        lines.append("This project is almost ready. Complete the missing sections and verify deployment before submission.")
    else:
        lines.append("This project needs more completion before final submission. Generate missing blueprint, command, debug, safety, and GPU sections.")

    return "\n".join(lines)


def get_included_artifacts(
    blueprint=None,
    commands=None,
    debug_result=None,
    gpu_result=None,
    safety_result=None,
):
    return [
        {
            "Artifact": "Project Blueprint",
            "Status": "Included" if blueprint else "Missing",
            "Details": "Architecture, features, tech stack, AMD notes" if blueprint else "Generate from Design & Build Flow",
        },
        {
            "Artifact": "Command Runbook",
            "Status": "Included" if commands else "Missing",
            "Details": "Setup, validation, run, deploy commands" if commands else "Generate from CommandFlow",
        },
        {
            "Artifact": "DebugFix Report",
            "Status": "Included" if debug_result else "Missing",
            "Details": "Error type, root cause, fixed code, test commands" if debug_result else "Analyze one ROCm/PyTorch error",
        },
        {
            "Artifact": "GPU Estimate",
            "Status": "Included" if gpu_result else "Missing",
            "Details": "VRAM, OOM risk, GPU comparison, optimization" if gpu_result else "Run GPU Estimate",
        },
        {
            "Artifact": "Safety Scan",
            "Status": "Included" if safety_result else "Missing",
            "Details": "Risk patterns, safety score, safe fixes" if safety_result else "Run Safety Guard",
        },
    ]


# Backward-compatible simple function
def build_report(project_name: str, blueprint=None, debug_result=None, gpu_result=None, safety_result=None):
    return build_full_project_report(
        project_name=project_name,
        blueprint=blueprint,
        commands=None,
        command_readiness=None,
        debug_result=debug_result,
        gpu_result=gpu_result,
        gpu_recommendation=None,
        gpu_optimized=None,
        gpu_comparison=None,
        safety_result=safety_result,
    )

