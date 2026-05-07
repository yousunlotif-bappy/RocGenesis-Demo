import os
import requests
from dotenv import load_dotenv


# Load local .env file
load_dotenv()


DEFAULT_QWEN_MODEL = "qwen/qwen-2.5-coder-32b-instruct"


def get_api_status():
    """
    Check whether Qwen/OpenRouter API key is available.
    This function never exposes the API key.
    """

    api_key = os.getenv("OPENROUTER_API_KEY")

    if api_key:
        return {
            "enabled": True,
            "provider": "OpenRouter",
            "model": DEFAULT_QWEN_MODEL,
            "message": "Qwen API is configured and ready.",
        }

    return {
        "enabled": False,
        "provider": "Fallback Mode",
        "model": "Rule-based RocGenesis fallback",
        "message": "OPENROUTER_API_KEY is not configured. RocGenesis will use fallback analysis.",
    }


def call_qwen(
    prompt: str,
    system_prompt: str = None,
    model: str = DEFAULT_QWEN_MODEL,
    temperature: float = 0.25,
    max_tokens: int = 1200,
) -> dict:
    """
    Call Qwen through OpenRouter.

    Returns a dictionary:
    {
        "ok": bool,
        "mode": "qwen" or "fallback",
        "content": str,
        "error": str or None,
        "model": str
    }

    This makes the app safe:
    - No API key = fallback mode
    - API error = fallback mode
    - App never crashes because of API issue
    """

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not prompt or not prompt.strip():
        return {
            "ok": False,
            "mode": "fallback",
            "content": "No prompt was provided for Qwen analysis.",
            "error": "Empty prompt",
            "model": "fallback",
        }

    if not api_key:
        return {
            "ok": False,
            "mode": "fallback",
            "content": (
                "Qwen API key is not configured. RocGenesis is running in fallback mode.\n\n"
                "To enable Qwen reasoning, add OPENROUTER_API_KEY to your .env file locally "
                "or to Hugging Face Space Secrets during deployment."
            ),
            "error": "Missing OPENROUTER_API_KEY",
            "model": "fallback",
        }

    if system_prompt is None:
        system_prompt = (
            "You are RocGenesis, an AMD-ready AI development copilot. "
            "You help developers debug ROCm, PyTorch, HIP, GPU memory, model serving, "
            "safe commands, AMD GPU deployment, and developer workflow issues. "
            "Give practical, concise, safe, developer-friendly answers."
        )

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://rocgenesis.local",
                "X-Title": "RocGenesis",
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=60,
        )

        response.raise_for_status()
        data = response.json()

        content = data["choices"][0]["message"]["content"]

        return {
            "ok": True,
            "mode": "qwen",
            "content": content,
            "error": None,
            "model": model,
        }

    except requests.exceptions.Timeout:
        return {
            "ok": False,
            "mode": "fallback",
            "content": (
                "Qwen request timed out. RocGenesis fallback analysis is still available. "
                "Try again later or reduce the prompt size."
            ),
            "error": "Request timeout",
            "model": "fallback",
        }

    except requests.exceptions.HTTPError as e:
        return {
            "ok": False,
            "mode": "fallback",
            "content": (
                "Qwen API returned an HTTP error. RocGenesis fallback analysis is still available.\n\n"
                f"Error detail: {str(e)}"
            ),
            "error": str(e),
            "model": "fallback",
        }

    except Exception as e:
        return {
            "ok": False,
            "mode": "fallback",
            "content": (
                "Qwen request failed. RocGenesis fallback analysis is still available.\n\n"
                f"Error detail: {str(e)}"
            ),
            "error": str(e),
            "model": "fallback",
        }


def build_fallback_analysis(error_type: str, root_cause: str, fix_steps: list) -> str:
    """
    Deterministic fallback explanation when Qwen is not available.
    """

    lines = []

    lines.append("### RocGenesis Fallback Analysis")
    lines.append("")
    lines.append(f"**Detected issue:** {error_type}")
    lines.append("")
    lines.append(f"**Likely root cause:** {root_cause}")
    lines.append("")
    lines.append("**Practical fix checklist:**")

    for step in fix_steps:
        lines.append(f"- {step}")

    lines.append("")
    lines.append("**AMD/ROCm validation checklist:**")
    lines.append("- Run `rocm-smi` to verify AMD GPU visibility and VRAM usage.")
    lines.append("- Run `rocminfo` to confirm ROCm can detect the device.")
    lines.append("- Check `torch.version.hip` to verify ROCm-enabled PyTorch.")
    lines.append("- Re-run the workload with lower memory pressure.")
    lines.append("- Export the DebugFix report after validation.")

    return "\n".join(lines)

