import os
import pandas as pd
import streamlit as st

from agents.design_agent import generate_blueprint
from agents.command_agent import (
    generate_command_runbook,
    calculate_command_readiness,
    build_command_script,
    build_command_report,
)
from agents.debug_agent import analyze_error
from agents.gpu_estimator import (
    estimate_vram,
    get_gpu_recommendation,
    optimization_tips,
    estimate_optimized_vram,
    compare_gpus,
    build_gpu_report,
)
from agents.report_agent import (
    build_full_project_report,
    calculate_report_scores,
    get_included_artifacts,
)
from utils.safety_rules import scan_text_safety, build_safety_report
from utils.llm_client import get_api_status


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="RocGenesis",
    page_icon="🚀",
    layout="wide",
)


# =========================
# GLOBAL CSS
# =========================
st.markdown(
    """
<style>
:root {
    --cyan: #38BDF8;
    --cyan-soft: #7DD3FC;
    --orange: #F59E0B;
    --green: #86EFAC;
    --text: #EAF2FF;
    --muted: #94A3B8;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(14,165,233,0.14) 0%, transparent 32%),
        radial-gradient(circle at top right, rgba(245,158,11,0.08) 0%, transparent 26%),
        linear-gradient(135deg, #020617 0%, #050914 45%, #02040A 100%);
    color: var(--text);
}

.block-container {
    padding-top: 2.2rem;
    padding-bottom: 3rem;
    max-width: 1320px;
}

section[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at top left, rgba(56,189,248,0.16), transparent 32%),
        linear-gradient(180deg, #07152B 0%, #03101F 55%, #020617 100%);
    border-right: 1px solid rgba(56,189,248,0.28);
}

section[data-testid="stSidebar"] * {
    color: #EAF2FF;
}

div[data-testid="stAppViewContainer"] main h1 {
    font-size: 56px !important;
    font-weight: 950 !important;
    letter-spacing: -1.5px;
    margin-bottom: 0.2rem;
    background: linear-gradient(90deg, #7DD3FC, #FFFFFF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

h2, h3 {
    color: #EAF2FF !important;
}

p, li, span, div {
    color: #DCEBFF;
}

hr {
    border-color: rgba(56,189,248,0.22);
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(8,34,65,0.92), rgba(5,15,30,0.96));
    border: 1px solid rgba(56,189,248,0.25);
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 0 25px rgba(56,189,248,0.08);
}

[data-testid="stMetricValue"] {
    font-size: 28px !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
}

[data-testid="stMetricLabel"] {
    color: #B7C4D6 !important;
    white-space: normal !important;
}

div[data-testid="stAlert"] {
    background: linear-gradient(145deg, rgba(8,34,65,0.95), rgba(6,18,35,0.95));
    border: 1px solid rgba(56,189,248,0.28);
    border-radius: 18px;
    color: #EAF2FF;
}

.stButton > button {
    background: linear-gradient(90deg, #0369A1, #2563EB);
    color: white;
    border: 1px solid rgba(125,211,252,0.45);
    border-radius: 13px;
    padding: 0.7rem 1.2rem;
    font-weight: 800;
    box-shadow: 0 0 18px rgba(37,99,235,0.25);
}

.stButton > button:hover {
    background: linear-gradient(90deg, #0284C7, #1D4ED8);
    border: 1px solid #7DD3FC;
    color: white;
}

.stDownloadButton > button {
    background: linear-gradient(90deg, #0F766E, #0891B2);
    color: white;
    border: 1px solid rgba(125,211,252,0.45);
    border-radius: 13px;
    padding: 0.7rem 1.2rem;
    font-weight: 800;
}

textarea, input, select {
    background-color: #07152B !important;
    color: #EAF2FF !important;
    border-radius: 12px !important;
}

code {
    color: #7DD3FC !important;
}

footer {
    visibility: hidden;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: transparent;
    border-radius: 12px;
    padding: 9px 10px;
    margin: 2px 0;
    transition: 0.2s ease;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(56,189,248,0.10);
}

.roc-card {
    background: linear-gradient(145deg, rgba(8,34,65,0.92), rgba(5,15,30,0.96));
    border: 1px solid rgba(56,189,248,0.27);
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 0 28px rgba(56,189,248,0.08);
    min-height: 145px;
    overflow: hidden;
}

.roc-card-orange {
    border: 1px solid rgba(245,158,11,0.42);
}

.roc-label {
    color: #B7C4D6;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 8px;
}

.roc-value {
    color: #EAF2FF;
    font-size: 24px;
    font-weight: 900;
    line-height: 1.15;
    word-break: keep-all;
    overflow-wrap: normal;
    white-space: normal;
}

.roc-sub {
    color: #86EFAC;
    font-size: 14px;
    margin-top: 10px;
    font-weight: 700;
}

.roc-badge {
    display: inline-block;
    padding: 7px 11px;
    border-radius: 999px;
    background: rgba(20,184,166,0.16);
    border: 1px solid rgba(45,212,191,0.35);
    color: #99F6E4;
    font-weight: 800;
    font-size: 13px;
    margin-right: 8px;
    margin-bottom: 8px;
}

.roc-badge-orange {
    background: rgba(245,158,11,0.13);
    border: 1px solid rgba(245,158,11,0.36);
    color: #FCD34D;
}

.roc-badge-red {
    background: rgba(251,113,133,0.13);
    border: 1px solid rgba(251,113,133,0.36);
    color: #FDA4AF;
}

.roc-hero {
    background:
        radial-gradient(circle at top right, rgba(56,189,248,0.14), transparent 35%),
        linear-gradient(145deg, rgba(8,34,65,0.72), rgba(5,15,30,0.82));
    border: 1px solid rgba(56,189,248,0.25);
    border-radius: 24px;
    padding: 28px;
    box-shadow: 0 0 32px rgba(56,189,248,0.07);
}

.sidebar-mini-card {
    background: linear-gradient(145deg, rgba(8,34,65,0.75), rgba(5,15,30,0.95));
    border: 1px solid rgba(56,189,248,0.38);
    border-radius: 14px;
    padding: 12px 16px;
    margin: 6px 0 22px 0;
    box-shadow: 0 0 18px rgba(56,189,248,0.08);
}

.sidebar-section-title {
    color:#94A3B8;
    font-size:0.78rem;
    font-weight:900;
    letter-spacing:1.2px;
    text-transform:uppercase;
    margin: 10px 0 10px 0;
}

.sidebar-feature {
    display:flex;
    align-items:center;
    gap:12px;
    color:#CBD5E1;
    font-size:0.92rem;
    margin-bottom: 13px;
}

.sidebar-bottom-card {
    background: linear-gradient(145deg, rgba(8,34,65,0.88), rgba(5,15,30,0.96));
    border: 1px solid rgba(56,189,248,0.30);
    border-radius: 18px;
    padding: 16px 18px;
    margin-top: 10px;
    box-shadow: 0 0 24px rgba(56,189,248,0.08);
    position: relative;
}

.sidebar-bottom-line {
    position:absolute;
    left:14px;
    top:18px;
    bottom:18px;
    width:3px;
    border-radius:999px;
    background: linear-gradient(180deg, #22D3EE, #34D399);
}


/* Polished sidebar navigation */
section[data-testid="stSidebar"] {
    width: 320px !important;
}

section[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.15rem;
}

section[data-testid="stSidebar"] img {
    display: block;
    margin: 0 auto 1.15rem auto;
    border-radius: 14px;
    opacity: 0.96;
}

section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 6px;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label {
    min-height: 46px;
    background: rgba(8,34,65,0.20);
    border: 1px solid rgba(56,189,248,0.00);
    border-radius: 14px;
    padding: 10px 12px !important;
    margin: 3px 0 !important;
    transition: all 0.18s ease;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(56,189,248,0.10);
    border: 1px solid rgba(56,189,248,0.22);
    transform: translateX(2px);
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(90deg, rgba(14,165,233,0.34), rgba(37,99,235,0.17));
    border: 1px solid rgba(125,211,252,0.45);
    box-shadow: inset 3px 0 0 #38BDF8, 0 0 20px rgba(56,189,248,0.12);
}

section[data-testid="stSidebar"] div[role="radiogroup"] label p {
    font-size: 0.96rem !important;
    font-weight: 750 !important;
    letter-spacing: -0.1px;
}

.sidebar-section-title {
    color:#8FB7D8;
    font-size:0.72rem;
    font-weight:950;
    letter-spacing:1.55px;
    text-transform:uppercase;
    margin: 18px 0 12px 0;
}

.sidebar-feature-card {
    display:flex;
    align-items:flex-start;
    gap:12px;
    padding: 11px 12px;
    margin-bottom: 9px;
    border-radius: 14px;
    background: rgba(8,34,65,0.18);
    border: 1px solid rgba(56,189,248,0.10);
}

.sidebar-feature-card:hover {
    background: rgba(56,189,248,0.09);
    border-color: rgba(56,189,248,0.24);
}

.sidebar-feature-icon {
    width: 24px;
    height: 24px;
    border-radius: 8px;
    display:flex;
    align-items:center;
    justify-content:center;
    background: rgba(56,189,248,0.12);
    border: 1px solid rgba(56,189,248,0.20);
    color: #7DD3FC;
    font-weight:900;
    flex: 0 0 auto;
}

.sidebar-feature-title {
    color:#EAF2FF;
    font-size:0.88rem;
    font-weight:850;
    line-height:1.25;
}

.sidebar-feature-sub {
    color:#8EA4BB;
    font-size:0.72rem;
    line-height:1.35;
    margin-top:2px;
}

.sidebar-status-card {
    background: linear-gradient(145deg, rgba(8,34,65,0.88), rgba(5,15,30,0.98));
    border: 1px solid rgba(56,189,248,0.28);
    border-radius: 18px;
    padding: 16px 18px;
    margin-top: 18px;
    box-shadow: 0 0 24px rgba(56,189,248,0.08);
}

.sidebar-status-title {
    color:#EAF2FF;
    font-size:1.02rem;
    font-weight:950;
    margin-bottom:4px;
}

.sidebar-status-sub {
    color:#9FB3C8;
    font-size:0.80rem;
    margin-bottom:14px;
}

.sidebar-api-pill {
    background: rgba(16,185,129,0.16);
    border: 1px solid rgba(52,211,153,0.34);
    color: #34D399;
    border-radius: 14px;
    padding: 10px 12px;
    font-weight:900;
    margin-bottom:10px;
}

.sidebar-model-text {
    color:#CBD5E1;
    font-size:0.74rem;
    line-height:1.35;
    word-break:break-word;
}

.workflow-panel {
    background: linear-gradient(145deg, rgba(8,34,65,0.98), rgba(5,15,30,0.98));
    border: 1px solid rgba(56,189,248,0.35);
    border-radius: 22px;
    padding: 24px;
    box-shadow: 0 0 28px rgba(56,189,248,0.07);
}

.workflow-grid {
    display: grid;
    grid-template-columns: repeat(7, minmax(110px, 1fr));
    gap: 12px;
    align-items: stretch;
}

.workflow-step {
    position: relative;
    background: rgba(8,34,65,0.85);
    border: 1px solid rgba(56,189,248,0.30);
    border-radius: 16px;
    padding: 16px 12px;
    text-align: center;
    min-height: 112px;
}

.workflow-step.final {
    border-color: rgba(245,158,11,0.48);
}

.workflow-num {
    color:#7DD3FC;
    font-size:12px;
    font-weight:950;
    margin-bottom:5px;
}

.workflow-step.final .workflow-num {
    color:#F59E0B;
}

.workflow-title {
    color:#EAF2FF;
    font-size:15px;
    font-weight:950;
    line-height:1.2;
}

.workflow-sub {
    color:#94A3B8;
    font-size:12px;
    line-height:1.35;
    margin-top:8px;
}


.quick-action-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(180px, 1fr));
    gap: 16px;
    margin-top: 12px;
    margin-bottom: 20px;
}

.quick-action-card {
    background: linear-gradient(145deg, rgba(8,34,65,0.92), rgba(5,15,30,0.98));
    border: 1px solid rgba(56,189,248,0.26);
    border-radius: 18px;
    padding: 18px;
    min-height: 128px;
    box-shadow: 0 0 22px rgba(56,189,248,0.06);
}

.quick-action-title {
    color: #EAF2FF;
    font-size: 16px;
    font-weight: 950;
    margin-bottom: 8px;
}

.quick-action-sub {
    color: #9FB3C8;
    font-size: 13px;
    line-height: 1.45;
}

.workflow-panel {
    padding: 28px;
}

.workflow-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(160px, 1fr));
    gap: 16px;
    align-items: stretch;
}

.workflow-step {
    text-align: left;
    min-height: 138px;
    padding: 18px;
}

.workflow-step::after {
    content: "";
    position: absolute;
    right: -14px;
    top: 50%;
    width: 12px;
    height: 2px;
    background: linear-gradient(90deg, rgba(56,189,248,0.75), transparent);
}

.workflow-step:nth-child(4)::after,
.workflow-step:nth-child(7)::after {
    display: none;
}

.workflow-step.final {
    background: linear-gradient(145deg, rgba(30,18,4,0.68), rgba(8,34,65,0.88));
}

.workflow-title {
    font-size: 16px;
}

.workflow-sub {
    font-size: 13px;
    margin-top: 10px;
}

.workflow-tag {
    display:inline-block;
    margin-top: 12px;
    padding: 5px 9px;
    border-radius: 999px;
    background: rgba(56,189,248,0.10);
    border: 1px solid rgba(56,189,248,0.24);
    color: #7DD3FC;
    font-size: 11px;
    font-weight: 900;
}

@media (max-width: 1100px) {
    .quick-action-grid { grid-template-columns: repeat(2, minmax(150px, 1fr)); }
}

@media (max-width: 1100px) {
    .workflow-grid { grid-template-columns: repeat(2, minmax(150px, 1fr)); }
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================
# SESSION STATE
# =========================
defaults = {
    "blueprint": None,
    "debug_result": None,
    "gpu_result": None,
    "gpu_recommendation": None,
    "gpu_tips": None,
    "gpu_optimized": None,
    "gpu_comparison": None,
    "gpu_report": None,
    "safety_result": None,
    "safety_report": None,
    "commands": None,
    "command_readiness": None,
    "final_report": None,
    "report_scores": None,
    "included_artifacts": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================
# UI HELPERS
# =========================
def header(subtitle="Agentic Debugging + GPU Workload Optimizer for AMD AI Developers"):
    st.title("RocGenesis")
    st.caption(subtitle)


def custom_metric(label, value, sub="", accent="cyan", orange=False):
    border_class = "roc-card-orange" if orange else ""
    color = "#F59E0B" if accent == "orange" else "#86EFAC" if accent == "green" else "#EAF2FF"
    st.markdown(
        f"""
<div class="roc-card {border_class}">
    <div class="roc-label">{label}</div>
    <div class="roc-value" style="color:{color};">{value}</div>
    <div class="roc-sub">{sub}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def module_card(number, title, description, points):
    bullet_points = "".join([f"<li>{p}</li>" for p in points])
    st.markdown(
        f"""
<div class="roc-card" style="min-height:260px; margin-bottom:18px;">
    <div style="color:#7DD3FC; font-size:15px; font-weight:900;">{number}</div>
    <h3 style="margin-top:4px; margin-bottom:8px;">{title}</h3>
    <p style="color:#B7C4D6; font-size:15px; min-height:48px;">{description}</p>
    <ul style="color:#DCEBFF; font-size:14px; line-height:1.8;">{bullet_points}</ul>
</div>
""",
        unsafe_allow_html=True,
    )


def badges(items):
    html = ""
    for text, kind in items:
        cls = "roc-badge"
        if kind == "orange":
            cls += " roc-badge-orange"
        elif kind == "red":
            cls += " roc-badge-red"
        html += f'<span class="{cls}">{text}</span>'
    st.markdown(html, unsafe_allow_html=True)


def professional_workflow():
    st.markdown(
        """<div class="workflow-panel">
<div style="display:flex; justify-content:space-between; align-items:flex-start; gap:18px; margin-bottom:18px;">
<div>
<div style="color:#7DD3FC; font-size:13px; font-weight:950; letter-spacing:1px; text-transform:uppercase;">End-to-end build lifecycle</div>
<div style="color:#EAF2FF; font-size:24px; font-weight:950; margin-top:4px;">From idea to AMD-ready deployment</div>
</div>
<div style="color:#86EFAC; font-size:13px; font-weight:900; padding:8px 12px; border-radius:999px; border:1px solid rgba(134,239,172,0.35); background:rgba(34,197,94,0.10);">Judge-ready flow</div>
</div>
<div class="workflow-grid">
<div class="workflow-step"><div class="workflow-num">01</div><div class="workflow-title">Idea Intake</div><div class="workflow-sub">Capture use case, users, model, and deployment target.</div><div class="workflow-tag">Input</div></div>
<div class="workflow-step"><div class="workflow-num">02</div><div class="workflow-title">AI Blueprint</div><div class="workflow-sub">Generate architecture, file structure, and AMD-ready plan.</div><div class="workflow-tag">Plan</div></div>
<div class="workflow-step"><div class="workflow-num">03</div><div class="workflow-title">CommandFlow</div><div class="workflow-sub">Create safe setup, run, test, and deploy commands.</div><div class="workflow-tag">Build</div></div>
<div class="workflow-step"><div class="workflow-num">04</div><div class="workflow-title">DebugFix</div><div class="workflow-sub">Explain ROCm/PyTorch errors and generate fixes.</div><div class="workflow-tag">Repair</div></div>
<div class="workflow-step"><div class="workflow-num">05</div><div class="workflow-title">Safety Guard</div><div class="workflow-sub">Scan commands, code, secrets, and risky patterns.</div><div class="workflow-tag">Secure</div></div>
<div class="workflow-step"><div class="workflow-num">06</div><div class="workflow-title">GPU Estimate</div><div class="workflow-sub">Estimate VRAM, OOM risk, AMD fit, and optimization tips.</div><div class="workflow-tag">Optimize</div></div>
<div class="workflow-step final"><div class="workflow-num">07</div><div class="workflow-title">Final Report</div><div class="workflow-sub">Export project evidence for README, demo, and judging.</div><div class="workflow-tag">Ship</div></div>
</div>
</div>""",
        unsafe_allow_html=True,
    )


def quick_actions():
    st.markdown(
        """
<div class="quick-action-grid">
    <div class="quick-action-card">
        <div class="quick-action-title">Start Blueprint</div>
        <div class="quick-action-sub">Turn a raw idea into an AMD-ready architecture and file structure.</div>
    </div>
    <div class="quick-action-card">
        <div class="quick-action-title">Generate Commands</div>
        <div class="quick-action-sub">Create setup, validation, run, test, and deploy commands safely.</div>
    </div>
    <div class="quick-action-card">
        <div class="quick-action-title">Debug ROCm Error</div>
        <div class="quick-action-sub">Analyze PyTorch/HIP errors with root cause, fix, and test commands.</div>
    </div>
    <div class="quick-action-card">
        <div class="quick-action-title">Export Final Report</div>
        <div class="quick-action-sub">Prepare judge-ready project, safety, GPU, and deployment evidence.</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        if st.button("Open Blueprint", use_container_width=True):
            st.session_state["pending_page_label"] = "Design & Build Flow"
            st.rerun()
    with b2:
        if st.button("Open CommandFlow", use_container_width=True):
            st.session_state["pending_page_label"] = "CommandFlow"
            st.rerun()
    with b3:
        if st.button("Open DebugFix", use_container_width=True):
            st.session_state["pending_page_label"] = "DebugFix"
            st.rerun()
    with b4:
        if st.button("Open Reports", use_container_width=True):
            st.session_state["pending_page_label"] = "Reports"
            st.rerun()


def make_debug_report(result):
    lines = ["# RocGenesis DebugFix Report", ""]
    lines += ["## Error Type", str(result.get("error_type", "Unknown")), ""]
    lines += ["## Root Cause", str(result.get("root_cause", "No root cause available.")), ""]
    lines += ["## Plain-language Explanation", str(result.get("plain_explanation", "No explanation available.")), ""]
    lines += ["## Risk Level", str(result.get("risk_level", "Unknown")), ""]
    lines += ["## Safety Score", f"{result.get('safety_score', 80)}/100", ""]
    lines += ["## Resolution Confidence", str(result.get("resolution_confidence", "70%")), ""]
    lines.append("## Fix Steps")
    for step in result.get("fix_steps", []):
        lines.append(f"- {step}")
    lines += ["", "## Test Commands"]
    for cmd in result.get("commands", []):
        lines += ["```bash", str(cmd), "```"]
    lines += ["", "## Fixed Code", "```python", str(result.get("fixed_code", "# No fixed code available.")), "```"]
    lines += ["", "## Qwen Deep Analysis", str(result.get("qwen_analysis", "Qwen analysis not available."))]
    return "\n".join(lines)


# =========================
# PREMIUM SIDEBAR
# =========================
logo_candidates = [
    "assets/logo_clean.png",
    "assets/logo_clean.png",
    "assets/logo_clean.png",
    "assets/logo_clean.png",
]
logo_path = next((path for path in logo_candidates if os.path.exists(path)), None)

NAV_ITEMS = {
    "Dashboard": "Dashboard",
    "Design & Build Flow": "Design & Build Flow",
    "CommandFlow": "CommandFlow",
    "DebugFix": "DebugFix",
    "Safety Guard": "Safety Guard",
    "GPU Estimate": "GPU Estimate",
    "Reports": "Reports",
    "Settings": "Settings",
}

with st.sidebar:
    if logo_path:
        st.image(logo_path, width=230)
    else:
        st.markdown("### RocGenesis")
        st.caption("AMD-ready AI Development Copilot")

    st.markdown('<div class="sidebar-section-title">Navigation</div>', unsafe_allow_html=True)

if "page_label" not in st.session_state:
    st.session_state["page_label"] = "Dashboard"

# Apply page change requested by Quick Actions BEFORE creating the radio widget.
if "pending_page_label" in st.session_state:
    st.session_state["page_label"] = st.session_state.pop("pending_page_label")

page_label = st.sidebar.radio(
    "Navigation",
    list(NAV_ITEMS.keys()),
    label_visibility="collapsed",
    key="page_label",
)
page = NAV_ITEMS[page_label]

with st.sidebar:
    st.divider()
    st.markdown('<div class="sidebar-section-title">Features</div>', unsafe_allow_html=True)

    st.markdown(
        """<div class="sidebar-feature-card"><div class="sidebar-feature-icon">01</div><div><div class="sidebar-feature-title">AI Project Blueprinting</div><div class="sidebar-feature-sub">Idea to AMD-ready project plan</div></div></div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """<div class="sidebar-feature-card"><div class="sidebar-feature-icon">02</div><div><div class="sidebar-feature-title">Smart Debug Assistant</div><div class="sidebar-feature-sub">ROCm/PyTorch error reasoning</div></div></div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """<div class="sidebar-feature-card"><div class="sidebar-feature-icon">03</div><div><div class="sidebar-feature-title">GPU Workload Optimizer</div><div class="sidebar-feature-sub">VRAM, OOM, and fit estimate</div></div></div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """<div class="sidebar-feature-card"><div class="sidebar-feature-icon">04</div><div><div class="sidebar-feature-title">Deployment Readiness</div><div class="sidebar-feature-sub">Safety and report export</div></div></div>""",
        unsafe_allow_html=True,
    )

    api_status = get_api_status()
    api_text = "Qwen API: Active" if api_status["enabled"] else "Qwen API: Fallback"
    model_text = api_status["model"] if api_status["enabled"] else "Add OPENROUTER_API_KEY in .env"

    st.markdown(
        f"""<div class="sidebar-status-card"><div class="sidebar-status-title">RocGenesis</div><div class="sidebar-status-sub">AMD-ready Development Copilot</div><div class="sidebar-api-pill">{api_text}</div><div class="sidebar-model-text">Model: {model_text}</div></div>""",
        unsafe_allow_html=True,
    )



# =========================
# DASHBOARD
# =========================
if page == "Dashboard":
    header()

    st.markdown(
        """
<div class="roc-hero">
    <h2 style="margin-top:0;">Build, debug, secure, optimize, and ship AI apps on AMD GPUs.</h2>
    <p style="font-size:17px; color:#B7C4D6; max-width:980px;">
    RocGenesis is an AMD-ready AI development copilot that guides developers from raw idea to
    deployment-ready AI project using structured planning, safe commands, ROCm/PyTorch debugging,
    GPU workload estimation, safety scanning, and final report export.
    </p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.write("")
    c1, c2, c3, c4 = st.columns([1.3, 1.05, 1.2, 1.05])
    with c1:
        custom_metric("Project Health", "Excellent", "On Track", "green")
    with c2:
        custom_metric("Safety Score", "92/100", "Safe", "green")
    with c3:
        custom_metric("GPU Status", "AMD-ready", "Healthy", "cyan")
    with c4:
        custom_metric("Deploy Readiness", "94%", "Ready", "orange", orange=True)

    st.divider()
    st.subheader("Quick Actions")
    quick_actions()

    st.divider()
    st.subheader("Why RocGenesis Stands Out")

    w1, w2, w3 = st.columns(3)

    with w1:
        st.markdown(
            """
<div class="roc-card">
    <div style="color:#7DD3FC; font-size:15px; font-weight:900; margin-bottom:10px;">01</div>
    <h3>AMD-ready by Design</h3>
    <p style="color:#B7C4D6; font-size:15px; line-height:1.6;">
        RocGenesis is built around AMD GPU workflows, ROCm-aware setup, PyTorch ROCm checks,
        and deployment guidance for AMD-powered AI applications.
    </p>
</div>
""",
            unsafe_allow_html=True,
        )

    with w2:
        st.markdown(
            """
<div class="roc-card">
    <div style="color:#7DD3FC; font-size:15px; font-weight:900; margin-bottom:10px;">02</div>
    <h3>Agentic Developer Workflow</h3>
    <p style="color:#B7C4D6; font-size:15px; line-height:1.6;">
        It connects planning, command generation, debugging, safety review,
        GPU estimation, and reporting into one guided AI development lifecycle.
    </p>
</div>
""",
            unsafe_allow_html=True,
        )

    with w3:
        st.markdown(
            """
<div class="roc-card roc-card-orange">
    <div style="color:#F59E0B; font-size:15px; font-weight:900; margin-bottom:10px;">03</div>
    <h3>Submission-ready Output</h3>
    <p style="color:#B7C4D6; font-size:15px; line-height:1.6;">
        The app can generate command runbooks, safety notes, GPU reports,
        DebugFix explanations, and a final judge-ready project report.
    </p>
</div>
""",
            unsafe_allow_html=True,
        )

    st.divider()
    st.subheader("Module Summary")

    m1, m2, m3 = st.columns(3)
    with m1:
        module_card(
            "01",
            "Design & Build Flow",
            "Turn raw ideas into AMD-ready project blueprints.",
            ["Analyze idea and requirements", "Generate architecture", "Suggest file structure", "Add AMD/ROCm best practices"],
        )
    with m2:
        module_card(
            "02",
            "CommandFlow",
            "Generate safe setup, run, test, and deploy commands.",
            ["Step-by-step terminal commands", "Command explanation", "ROCm environment checks", "Export command runbook"],
        )
    with m3:
        module_card(
            "03",
            "DebugFix",
            "Explain ROCm/PyTorch errors and suggest fixes.",
            ["Detect root cause", "Explain in simple language", "Generate ROCm-friendly fix", "Show test commands"],
        )

    m4, m5, m6 = st.columns(3)
    with m4:
        module_card(
            "04",
            "Safety Guard",
            "Detect risky code, commands, secrets, and unsafe patterns.",
            ["Command safety scan", "Secret detection", "Risk score", "Safe alternatives"],
        )
    with m5:
        module_card(
            "05",
            "GPU Estimate",
            "Estimate VRAM, OOM risk, and optimization strategy.",
            ["VRAM estimation", "OOM risk prediction", "AMD GPU fit score", "Optimization tips"],
        )
    with m6:
        module_card(
            "06",
            "Reports",
            "Generate project, safety, GPU, and deployment reports.",
            ["Final summary", "Debug report", "GPU report", "Download Markdown report"],
        )

    st.divider()
    st.subheader("Professional Workflow")
    professional_workflow()


# =========================
# DESIGN & BUILD FLOW
# =========================
elif page == "Design & Build Flow":
    header()
    st.header("Design & Build Flow")
    st.write("Transform your raw idea into an AMD-ready AI project blueprint.")

    project_idea = st.text_area(
        "Raw Project Idea",
        value="I want to build a multimodal chatbot that analyzes images and answers questions using AMD GPUs.",
        height=140,
    )

    col1, col2 = st.columns(2)
    with col1:
        target_users = st.text_input("Target Users", value="AI developers, researchers, students")
        model_name = st.selectbox("Model", ["Qwen", "Qwen-VL", "Llama 3.1/3.2", "Mistral", "DeepSeek"])
    with col2:
        deployment_target = st.selectbox("Deployment Target", ["Hugging Face Space", "Docker", "Local", "AMD Developer Cloud"])
        framework = st.selectbox("Framework", ["Streamlit", "Gradio", "FastAPI", "Next.js + FastAPI"])

    if st.button("Generate AMD-ready Blueprint", use_container_width=True):
        st.session_state.blueprint = generate_blueprint(
            project_idea=project_idea,
            target_users=target_users,
            model_name=model_name,
            deployment_target=deployment_target,
        )

    if st.session_state.blueprint:
        bp = st.session_state.blueprint
        st.success("Blueprint generated successfully.")

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Project Summary")
            st.write(bp["summary"])
            st.subheader("Core Features")
            for item in bp["core_features"]:
                st.write(f"✅ {item}")

        with c2:
            st.subheader("Recommended Tech Stack")
            for item in bp["tech_stack"]:
                st.write(f"🔹 {item}")
            st.subheader("Next Step")
            st.info(bp["next_step"])

        st.subheader("Architecture")
        st.write(" → ".join(bp["architecture"]))

        st.subheader("Suggested File Structure")
        st.code("\n".join(bp["file_structure"]), language="text")

        st.subheader("AMD / ROCm Optimization Notes")
        for note in bp["amd_notes"]:
            st.write(f"⚡ {note}")


# =========================
# COMMANDFLOW
# =========================
elif page == "CommandFlow":
    header()
    st.header("CommandFlow")
    st.write("Generate safe, step-by-step terminal commands to scaffold, validate, run, test, and deploy an AMD-ready AI project.")

    col_context, col_config = st.columns([1.1, 2])

    with col_context:
        st.subheader("Project Context")
        project_name = st.text_input("Project Name", value="VisionChat AMD")
        project_goal = st.text_area(
            "Project Goal",
            value="RAG chatbot for PDFs with citations. Built with Qwen LLM, FAISS vector store, optimized for AMD GPUs using ROCm.",
            height=140,
        )

    with col_config:
        st.subheader("Command Presets")
        c1, c2, c3 = st.columns(3)
        with c1:
            os_name = st.selectbox("OS", ["Ubuntu 22.04", "Ubuntu 24.04", "Windows WSL2"])
            package_manager = st.selectbox("Package Manager", ["pip", "conda"])
        with c2:
            framework = st.selectbox("Framework", ["Streamlit", "Gradio", "FastAPI"])
            deployment_target = st.selectbox("Deployment Target", ["Hugging Face Space", "Docker", "Local"])
        with c3:
            gpu_target = st.selectbox(
                "GPU Target",
                ["AMD Instinct MI300X", "AMD Instinct MI250X", "AMD Radeon AI PRO R9700", "AMD Radeon RX 7900 XTX"],
            )

        generate_cmd = st.button("Generate Professional Command Runbook", use_container_width=True)

    if generate_cmd:
        commands = generate_command_runbook(project_name, framework, deployment_target, os_name, package_manager, gpu_target)
        st.session_state.commands = commands
        st.session_state.command_readiness = calculate_command_readiness(commands)

    if st.session_state.commands:
        commands = st.session_state.commands
        readiness = st.session_state.command_readiness or calculate_command_readiness(commands)

        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            custom_metric("Command Readiness", f"{readiness['score']}/100", readiness["level"], "green")
        with c2:
            custom_metric("Setup Time", readiness["estimated_time"], "Approx.", "cyan")
        with c3:
            custom_metric("Run Cost", readiness["estimated_cost"], "Per run estimate", "orange", orange=True)
        with c4:
            custom_metric("Commands", str(len(commands)), "Generated", "cyan")

        st.info(readiness["summary"])

        left, right = st.columns([1.45, 1])
        with left:
            st.subheader("Generated Command Runbook")
            for i, item in enumerate(commands, start=1):
                with st.expander(f"{i}. [{item.get('phase')}] {item.get('step')}", expanded=(i <= 3)):
                    st.code(item.get("command", ""), language="bash")
                    st.write(f"**What it does:** {item.get('explanation', '')}")
                    st.write(f"**Expected output:** {item.get('expected_output', '')}")
                    st.write(f"**AMD/ROCm note:** {item.get('amd_note', '')}")
                    st.write(f"**Risk level:** {item.get('risk', 'Low')}")

        with right:
            st.subheader("Command Safety Check")
            all_command_text = "\n".join([item.get("command", "") for item in commands])
            safety = scan_text_safety(all_command_text)
            st.metric("Safety Score", f"{safety['score']}/100")
            st.metric("Risk Level", safety["risk_level"])
            st.success("No destructive commands detected." if not safety["issues"] else safety["summary"])

            st.subheader("Recent AI Suggestions")
            st.write("• Pin dependency versions before final deployment.")
            st.write("• Validate ROCm visibility before model inference.")
            st.write("• Keep API keys in environment secrets.")
            st.write("• Add README setup instructions for judges.")

        st.subheader("Export Runbook")
        script_text = build_command_script(commands)
        report_text = build_command_report(commands, readiness)

        d1, d2 = st.columns(2)
        with d1:
            st.download_button(
                "Download Shell Script",
                data=script_text,
                file_name="rocgenesis_command_runbook.sh",
                mime="text/plain",
                use_container_width=True,
            )
        with d2:
            st.download_button(
                "Download Command Report",
                data=report_text,
                file_name="rocgenesis_commandflow_report.md",
                mime="text/markdown",
                use_container_width=True,
            )


# =========================
# DEBUGFIX
# =========================
elif page == "DebugFix":
    header()
    st.header("DebugFix")
    st.write("Professional ROCm/PyTorch/HIP error analysis with fixed code, validation commands, safety score, and Qwen-powered reasoning.")

    api_status = get_api_status()
    if api_status["enabled"]:
        badges([("Qwen Mode: Active", "green"), (f"Model: {api_status['model']}", "orange")])
    else:
        badges([("Qwen Mode: Fallback", "orange"), ("No API key detected", "red")])

    sample_error = """RuntimeError: HIP out of memory
hipErrorOutOfMemory: out of memory
"""

    col_input, col_settings = st.columns([2.2, 1])

    with col_input:
        error_log = st.text_area("Broken Code / Error Log", value=sample_error, height=250)

    with col_settings:
        st.subheader("Debug Settings")
        use_qwen = st.checkbox("Use Qwen Deep Analysis", value=True)
        framework = st.selectbox("Framework", ["PyTorch", "Transformers", "vLLM", "Gradio", "Streamlit"])
        gpu_target = st.selectbox("GPU Target", ["AMD Instinct MI300X", "AMD Instinct MI250X", "AMD Radeon AI PRO R9700", "AMD Radeon RX 7900 XTX"])
        rocm_version = st.text_input("ROCm Version", value="6.1.2")
        analyze_button = st.button("Run DebugFix Analysis", use_container_width=True)

    if analyze_button:
        with st.spinner("RocGenesis DebugFix is analyzing the error..."):
            st.session_state.debug_result = analyze_error(error_log, use_qwen=use_qwen)

    if st.session_state.debug_result:
        result = st.session_state.debug_result

        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            custom_metric("Error Type", result.get("error_type", "Unknown"), "Detected", "cyan")
        with c2:
            custom_metric("Risk Level", result.get("risk_level", "Unknown"), "Review", "orange", orange=True)
        with c3:
            custom_metric("Safety Score", f"{result.get('safety_score', 80)}/100", "Code safety", "green")
        with c4:
            custom_metric("Confidence", result.get("resolution_confidence", "70%"), "Fix estimate", "green")

        if result.get("qwen_api_ok"):
            st.success(f"Qwen analysis completed with {result.get('qwen_model')}.")
        else:
            st.warning("Running with RocGenesis fallback analysis. Add OPENROUTER_API_KEY for live Qwen reasoning.")

        st.subheader("Root Cause")
        st.write(result.get("root_cause", "No root cause available."))

        st.subheader("Plain-language Explanation")
        st.info(result.get("plain_explanation", "No explanation available."))

        left, right = st.columns([1.1, 1])
        with left:
            st.subheader("Step-by-step Fix")
            for step in result.get("fix_steps", []):
                st.write(f"✅ {step}")

            st.subheader("AMD / ROCm Notes")
            for note in result.get("amd_notes", []):
                st.write(f"⚡ {note}")

        with right:
            st.subheader("Test Commands")
            for command in result.get("commands", []):
                st.code(command, language="bash")

            st.subheader("What Changed")
            for change in result.get("what_changed", []):
                st.write(f"🔧 {change}")

        st.subheader("ROCm-friendly Fixed Code")
        st.code(result.get("fixed_code", "# No fixed code available."), language="python")

        st.subheader("Qwen Deep Analysis")
        st.markdown(result.get("qwen_analysis", "Qwen analysis not available."))

        debug_report = make_debug_report(result)
        st.download_button(
            "Download DebugFix Report",
            data=debug_report,
            file_name="rocgenesis_debugfix_report.md",
            mime="text/markdown",
            use_container_width=True,
        )


# =========================
# SAFETY GUARD
# =========================
elif page == "Safety Guard":
    header()
    st.header("Safety Guard")
    st.write("Professional safety review for code, commands, dependencies, model loading, secrets, and deployment configuration.")

    sample_safety_input = """from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "some-org/some-model",
    trust_remote_code=True
)

api_key = "sk-1234567890abcdef"
user_input = st.text_area("Prompt")
debug=True

# risky command example:
# curl https://example.com/install.sh | bash
"""

    col_input, col_settings = st.columns([2.1, 1])
    with col_input:
        safety_input = st.text_area("Paste code, commands, requirements, or deployment config", value=sample_safety_input, height=300)

    with col_settings:
        st.subheader("Scan Settings")
        scan_type = st.selectbox("Input Type", ["Auto-detect", "Python Code", "Shell Commands", "Requirements", "Deployment Config"])
        deployment_target = st.selectbox("Deployment Target", ["Hugging Face Space", "Docker", "Local", "AMD Developer Cloud"])
        strict_mode = st.checkbox("Strict Safety Mode", value=True)
        run_scan = st.button("Run Full Safety Scan", use_container_width=True)

    if run_scan:
        with st.spinner("Safety Guard is scanning for risks..."):
            scan_result = scan_text_safety(safety_input)
            st.session_state.safety_result = scan_result
            st.session_state.safety_report = build_safety_report(scan_result, safety_input)

    if st.session_state.safety_result:
        result = st.session_state.safety_result

        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            custom_metric("Safety Score", f"{result['score']}/100", "Scan result", "green")
        with c2:
            custom_metric("Risk Level", result["risk_level"], "Detected", "orange", orange=True)
        with c3:
            custom_metric("Issues Found", str(len(result["issues"])), "Total risks", "cyan")
        with c4:
            custom_metric("Deploy Status", result["deployment_readiness"], "Readiness", "green")

        if result["score"] >= 90:
            st.success(result["summary"])
        elif result["score"] >= 75:
            st.warning(result["summary"])
        else:
            st.error(result["summary"])

        left, right = st.columns([1.35, 1])

        with left:
            st.subheader("Detected Issues")
            if result["issues"]:
                issue_rows = []
                for issue in result["issues"]:
                    issue_rows.append(
                        {
                            "Category": issue["category"],
                            "Issue": issue["name"],
                            "Risk": issue["risk"],
                            "Matches": issue["matches_found"],
                            "Safe Fix": issue["safe_fix"],
                        }
                    )
                st.dataframe(pd.DataFrame(issue_rows), use_container_width=True, hide_index=True)

                st.subheader("Recommended Safe Fixes")
                for rec in result["recommendations"]:
                    if rec["risk"] == "High":
                        st.error(f"**[{rec['risk']}] {rec['issue']}** — {rec['fix']}")
                    elif rec["risk"] == "Medium":
                        st.warning(f"**[{rec['risk']}] {rec['issue']}** — {rec['fix']}")
                    else:
                        st.info(f"**[{rec['risk']}] {rec['issue']}** — {rec['fix']}")
            else:
                st.success("No critical issues detected.")

        with right:
            st.subheader("Issue Category Breakdown")
            category_counts = result.get("category_counts", {})
            if category_counts:
                st.table(pd.DataFrame([{"Category": k, "Count": v} for k, v in category_counts.items()]))
            else:
                st.info("No issue categories detected.")

            st.subheader("Risk Counts")
            st.write(f"High risk: **{result['high_count']}**")
            st.write(f"Medium risk: **{result['medium_count']}**")
            st.write(f"Low risk: **{result['low_count']}**")

            st.subheader("Best-practice Checklist")
            for item in result["checklist"]:
                st.write(f"✅ {item}")

        st.subheader("Export Safety Report")
        st.download_button(
            "Download Safety Guard Report",
            data=st.session_state.safety_report,
            file_name="rocgenesis_safety_guard_report.md",
            mime="text/markdown",
            use_container_width=True,
        )


# =========================
# GPU ESTIMATE
# =========================
elif page == "GPU Estimate":
    header()
    st.header("GPU Estimate")
    st.write("Estimate VRAM usage, OOM risk, AMD GPU suitability, and optimization impact before running your workload.")

    st.subheader("Model & Runtime Configuration")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        model_size = st.selectbox("Model Size", ["1", "3", "7", "8", "13", "34", "70"], index=6)
        precision = st.selectbox("Precision", ["fp32", "fp16", "bf16", "int8", "int4"], index=2)
    with c2:
        batch_size = st.number_input("Batch Size", min_value=1, value=1)
        sequence_length = st.number_input("Sequence Length", min_value=512, value=8192, step=512)
    with c3:
        task_type = st.selectbox("Task Type", ["Inference", "Fine-tuning", "Serving"])
        gpu_target = st.selectbox(
            "GPU Target",
            ["AMD Instinct MI300X - 192GB", "AMD Instinct MI250X - 128GB", "AMD Radeon AI PRO R9700 - 32GB", "AMD Radeon RX 7900 XTX - 24GB"],
        )
    with c4:
        rocm_version = st.text_input("ROCm Version", value="6.1.2")
        pytorch_version = st.text_input("PyTorch Version", value="2.4.0+rocm6.1")

    gpu_vram = 192
    selected_gpu_name = "AMD Instinct MI300X"
    if "MI250X" in gpu_target:
        gpu_vram = 128
        selected_gpu_name = "AMD Instinct MI250X"
    elif "R9700" in gpu_target:
        gpu_vram = 32
        selected_gpu_name = "AMD Radeon AI PRO R9700"
    elif "7900 XTX" in gpu_target:
        gpu_vram = 24
        selected_gpu_name = "AMD Radeon RX 7900 XTX"

    estimate_button = st.button("Run Professional GPU Estimate", use_container_width=True)

    if estimate_button:
        result = estimate_vram(float(model_size), precision, batch_size, sequence_length, task_type)
        recommendation = get_gpu_recommendation(result["total_memory_gb"], gpu_vram)
        tips = optimization_tips(precision, task_type, result["total_memory_gb"], gpu_vram)
        optimized = estimate_optimized_vram(result)
        comparison = compare_gpus(result["total_memory_gb"], task_type)

        st.session_state.gpu_result = result
        st.session_state.gpu_recommendation = recommendation
        st.session_state.gpu_tips = tips
        st.session_state.gpu_optimized = optimized
        st.session_state.gpu_comparison = comparison
        st.session_state.gpu_report = build_gpu_report(result, recommendation, comparison, tips, optimized)

    if st.session_state.gpu_result:
        result = st.session_state.gpu_result
        rec = st.session_state.gpu_recommendation
        tips = st.session_state.gpu_tips
        optimized = st.session_state.gpu_optimized
        comparison = st.session_state.gpu_comparison

        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            custom_metric("Estimated VRAM", f"{result['total_memory_gb']} GB", "Required memory", "cyan")
        with m2:
            custom_metric("GPU VRAM", f"{gpu_vram} GB", selected_gpu_name, "green")
        with m3:
            custom_metric("Utilization", f"{rec['utilization']}%", rec["status"], "orange", orange=True)
        with m4:
            custom_metric("OOM Risk", rec["risk"], rec["readiness"], "orange", orange=True)

        if rec["risk"] in ["High", "Critical"]:
            st.error(rec["advice"])
        elif rec["risk"] == "Medium":
            st.warning(rec["advice"])
        else:
            st.success(rec["advice"])

        left, right = st.columns([1.1, 1])
        with left:
            st.subheader("Memory Breakdown")
            breakdown_data = {
                "Component": ["Base Model Weights", "KV Cache", "Runtime Overhead", "Framework Overhead", "Total Estimated VRAM"],
                "Estimated Memory (GB)": [
                    result["base_memory_gb"],
                    result["kv_cache_gb"],
                    result["overhead_gb"],
                    result["framework_overhead_gb"],
                    result["total_memory_gb"],
                ],
            }
            st.table(pd.DataFrame(breakdown_data))

        with right:
            st.subheader("Before vs After Optimization")
            custom_metric("Before Optimization", f"{optimized['before_gb']} GB", "Current estimate", "orange", orange=True)
            st.write("")
            custom_metric("After Optimization", f"{optimized['after_gb']} GB", f"Saved {optimized['saved_gb']} GB", "green")

        st.subheader("AMD GPU Comparison")
        st.dataframe(pd.DataFrame(comparison), use_container_width=True, hide_index=True)

        st.subheader("Optimization Suggestions")
        for tip in tips:
            impact = tip["impact"]
            title = tip["title"]
            detail = tip["detail"]
            if impact in ["Critical", "High"]:
                st.warning(f"**[{impact}] {title}** — {detail}")
            else:
                st.info(f"**[{impact}] {title}** — {detail}")

        st.subheader("Export GPU Report")
        st.download_button(
            "Download GPU Estimate Report",
            data=st.session_state.gpu_report,
            file_name="rocgenesis_gpu_estimate_report.md",
            mime="text/markdown",
            use_container_width=True,
        )


# =========================
# REPORTS
# =========================
elif page == "Reports":
    header()
    st.header("Reports")
    st.write("Generate a final judge-ready report with project blueprint, commands, DebugFix, Safety Guard, GPU estimate, and deployment readiness.")

    project_name = st.text_input("Project Name", value="RocGenesis — AMD-ready AI Development Copilot")

    st.subheader("Report Scope")
    include_blueprint = st.checkbox("Include Project Blueprint", value=True)
    include_commands = st.checkbox("Include CommandFlow Runbook", value=True)
    include_debug = st.checkbox("Include DebugFix Report", value=True)
    include_safety = st.checkbox("Include Safety Guard Scan", value=True)
    include_gpu = st.checkbox("Include GPU Estimate", value=True)

    generate_report = st.button("Generate Final Judge-ready Report", use_container_width=True)

    if generate_report:
        blueprint = st.session_state.blueprint if include_blueprint else None
        commands = st.session_state.commands if include_commands else None
        debug_result = st.session_state.debug_result if include_debug else None
        safety_result = st.session_state.safety_result if include_safety else None
        gpu_result = st.session_state.gpu_result if include_gpu else None

        report = build_full_project_report(
            project_name=project_name,
            blueprint=blueprint,
            commands=commands,
            command_readiness=st.session_state.command_readiness,
            debug_result=debug_result,
            gpu_result=gpu_result,
            gpu_recommendation=st.session_state.gpu_recommendation,
            gpu_optimized=st.session_state.gpu_optimized,
            gpu_comparison=st.session_state.gpu_comparison,
            safety_result=safety_result,
        )

        scores = calculate_report_scores(
            blueprint=blueprint,
            commands=commands,
            debug_result=debug_result,
            gpu_result=gpu_result,
            safety_result=safety_result,
        )

        artifacts = get_included_artifacts(
            blueprint=blueprint,
            commands=commands,
            debug_result=debug_result,
            gpu_result=gpu_result,
            safety_result=safety_result,
        )

        st.session_state.final_report = report
        st.session_state.report_scores = scores
        st.session_state.included_artifacts = artifacts

    if st.session_state.final_report:
        scores = st.session_state.report_scores

        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            custom_metric("Completeness", f"{scores['completeness']}/100", "Report coverage", "green")
        with c2:
            custom_metric("Export Ready", f"{scores['export_readiness']}/100", "Download ready", "green")
        with c3:
            custom_metric("AMD Ready", f"{scores['amd_readiness']}/100", "ROCm aligned", "cyan")
        with c4:
            custom_metric("Deploy Ready", f"{scores['deployment_readiness']}/100", scores["readiness_label"], "orange", orange=True)

        if scores["deployment_readiness"] >= 90:
            st.success("Final report is ready for hackathon submission.")
        elif scores["deployment_readiness"] >= 75:
            st.warning("Final report is almost ready. Complete any missing artifacts before final submission.")
        else:
            st.error("Final report needs more work. Generate missing sections first.")

        left, right = st.columns([1.45, 1])
        with left:
            st.subheader("Generated Report Preview")
            st.markdown(st.session_state.final_report)

        with right:
            st.subheader("Included Artifacts")
            artifact_df = pd.DataFrame(st.session_state.included_artifacts)
            st.dataframe(artifact_df, use_container_width=True, hide_index=True)

            st.subheader("Recommended Next Steps")
            if not st.session_state.blueprint:
                st.write("• Generate a project blueprint from Design & Build Flow.")
            if not st.session_state.commands:
                st.write("• Generate CommandFlow runbook.")
            if not st.session_state.debug_result:
                st.write("• Run DebugFix with a ROCm/PyTorch error example.")
            if not st.session_state.gpu_result:
                st.write("• Run GPU Estimate.")
            if not st.session_state.safety_result:
                st.write("• Run Safety Guard scan.")
            st.write("• Add README, screenshots, and demo video before submission.")
            st.write("• Deploy to Hugging Face Space or provide a public demo link.")

            st.download_button(
                "Download Final Markdown Report",
                data=st.session_state.final_report,
                file_name="rocgenesis_final_project_report.md",
                mime="text/markdown",
                use_container_width=True,
            )


# =========================
# SETTINGS
# =========================
elif page == "Settings":
    header()
    st.header("Settings")

    api_status = get_api_status()

    c1, c2, c3 = st.columns(3)
    with c1:
        custom_metric(
            "Qwen API",
            "Active" if api_status["enabled"] else "Fallback",
            api_status["provider"],
            "green" if api_status["enabled"] else "orange",
            orange=not api_status["enabled"],
        )
    with c2:
        custom_metric("Model", api_status["model"], "Reasoning backend", "cyan")
    with c3:
        custom_metric("Safety Mode", "Strict", "Recommended", "green")

    st.subheader("Recommended Project Configuration")
    st.table(
        {
            "Setting": ["OS", "Framework", "Model", "GPU Target", "Deployment Target", "Safety Mode"],
            "Value": ["Ubuntu 22.04 LTS", "PyTorch + Streamlit", "Qwen / Llama", "AMD Instinct MI300X", "Hugging Face Space", "Strict"],
        }
    )

    st.info("For Hugging Face Space deployment, keep API keys in platform secrets, not inside the code.")



