import os
import json
from typing import Dict, Any, Optional

from schema import BriefAnalysis, ExecutionPlan
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()


# -------------------------------
# Azure Client
# -------------------------------
def get_azure_client(api_key: Optional[str] = None, endpoint: Optional[str] = None):
    key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
    base_url = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")

    if key and base_url:
        return AzureOpenAI(
            api_key=key,
            api_version="2024-02-01",
            azure_endpoint=base_url
        )
    return None


# -------------------------------
# MOCKS (must match schema)
# -------------------------------
def get_mock_analysis() -> Dict[str, Any]:
    return {
        "campaign_name": "Q3 Enterprise Trial-to-Paid Push",
        "objective": "Convert 200 enterprise trial accounts to paid contracts by end of Q3; generate 50 net-new demo requests.",
        "audience": "Trial users at 1000+ employee companies in Tech/Finance/Pro Services; VP Ops/RevOps/CMO.",
        "message": "Eliminate reporting lag so revenue teams act on what's happening now.",
        "channels": ["Email", "LinkedIn", "social", "sales outreach"],
        "budget": None,
        "timeline": "Campaign live by July 1; assets locked by June 20",
        "missing_fields": ["budget"],
        "ambiguities": ["'social' is unspecified (platforms + paid/organic)."],
        "clarification_questions": [
            "What is the approved total budget?",
            "Which social platforms are included in 'social' (and paid vs organic)?",
            "Should conversion messaging prioritize trial users, decision-makers, or both?"
        ]
    }


def get_mock_plan() -> Dict[str, Any]:
    return {
        "campaign_summary": "Multi-channel campaign to convert enterprise trials to paid and drive net-new demo requests.",

        # WOW fields
        "confidence_score": "8",
        "strengths": [
            "Clear conversion objective and audience definition",
            "Channel mix supports both conversion and net-new acquisition",
            "Strong constraints to prevent off-brand messaging"
        ],
        "risks": [
            "Budget was not provided; assumptions were used",
            "‘Social’ channel needs platform and paid/organic clarification",
            "Sales outreach targeting rules may require regional/account scoping"
        ],

        "assumptions": [
            "Assumed $15,000 total budget with heavier allocation to LinkedIn",
            "Assumed social includes LinkedIn + one secondary platform for retargeting"
        ],

        "channel_specifications": [
            {
                "channel": "Email - Trial Nurture",
                "format": "Lifecycle email sequence (3–5 touches)",
                "objective": "Convert active enterprise trial users to paid",
                "cta": "Book a Demo",
                "key_metrics": ["Open Rate", "CTR", "Trial-to-Paid Conversion"]
            }
        ],

        "milestones": [
            {"week": "Week 1", "date": "", "activity": "Kickoff planning and confirm goals/audience/budget", "deliverable": "Approved plan", "details": ""},
            {"week": "Week 2", "date": "", "activity": "Build audiences + draft compliant messaging", "deliverable": "Targeting + copy v1", "details": ""},
            {"week": "Week 3", "date": "", "activity": "Create assets + tracking framework", "deliverable": "Assets + UTM plan", "details": ""},
            {"week": "Week 4", "date": "", "activity": "QA + launch readiness", "deliverable": "QA sign-off", "details": ""}
        ],

        "copy_guidance_stubs": [
            "Tone: confident and direct, not aggressive.",
            "Do not reference competitors by name.",
            "Any time-savings claim must be supported by approved proof."
        ],

        "qa_checklist": [
            "Verify audience targeting matches 1000+ employee constraint",
            "Confirm CTA consistency per channel",
            "Validate UTMs and tracking on all links",
            "Check compliance with brand constraints"
        ]
    }


def get_mock_validation() -> Dict[str, Any]:
    return {
        "score": 7,
        "issues": [
            "Budget is not clearly allocated across channels",
            "Social channel is referenced but platforms (and paid vs organic) are not fully defined"
        ],
        "suggestions": [
            "Add an explicit per-channel budget split and resourcing assumptions",
            "Specify social platforms (e.g., LinkedIn paid + Instagram organic) and tailor format/copy per platform"
        ]
    }


# -------------------------------
# Analyze Brief
# -------------------------------
def analyze_brief(
    brief: str,
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    deployment: Optional[str] = None
) -> BriefAnalysis:
    client = get_azure_client(api_key, endpoint)
    model_name = deployment or "gpt-5.4-delta"

    if not client:
        return BriefAnalysis(**get_mock_analysis())

    prompt = f"""
You are a senior marketing campaign manager. Output MUST be JSON.

Analyze this campaign brief and extract fields.

Return JSON with these keys ONLY:
- campaign_name
- objective
- audience
- message
- channels
- budget
- timeline
- missing_fields
- ambiguities
- clarification_questions

IMPORTANT:
- objective MUST be a single string (no nested object)
- audience MUST be a single string (no nested object)
- timeline MUST be a single string (no nested object)

Brief:
{brief}
"""

    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return BriefAnalysis.model_validate_json(response.choices[0].message.content)


# -------------------------------
# Generate Execution Plan (enforce + repair 'format')
# -------------------------------
def generate_execution_plan(
    brief: str,
    answers: Dict[str, str],
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    deployment: Optional[str] = None
) -> ExecutionPlan:
    client = get_azure_client(api_key, endpoint)
    model_name = deployment or "gpt-5.4-delta"

    if not client:
        return ExecutionPlan(**get_mock_plan())

    answers_str = "\n".join([
        f"Q: {q}\nA: {a if a else 'No answer provided'}"
        for q, a in answers.items()
    ])

    prompt = f"""
You are a senior campaign strategist. Output MUST be JSON.

Create an execution plan.

Rules:
- Fill missing details using assumptions
- Each channel MUST include objective and CTA
- Each milestone MUST include a clear activity description (non-empty)
- Every channel_specification MUST include a non-empty "format" field (do not omit)

Also generate:
- confidence_score (1-10)
- strengths (3)
- risks (3)

Return JSON using exactly this structure:

{{
  "campaign_summary": "",

  "confidence_score": "",
  "strengths": [],
  "risks": [],

  "assumptions": [],

  "channel_specifications": [
    {{
      "channel": "",
      "format": "",
      "objective": "",
      "cta": "",
      "key_metrics": []
    }}
  ],

  "milestones": [
    {{
      "week": "",
      "date": "",
      "activity": "",
      "deliverable": "",
      "details": ""
    }}
  ],

  "copy_guidance_stubs": [],
  "qa_checklist": []
}}

Brief:
{brief}

Answers:
{answers_str}
"""

    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    raw = response.choices[0].message.content

    # Safe parse (prevents crash if model returns non-JSON text)
    try:
        data = json.loads(raw)
    except Exception:
        return ExecutionPlan(**get_mock_plan())

    # --- Minimal repair: ensure required keys exist (prevents Pydantic crash) ---
    if isinstance(data, dict) and "channel_specifications" in data and isinstance(data["channel_specifications"], list):
        for spec in data["channel_specifications"]:
            if isinstance(spec, dict):
                # Fill missing 'format' to satisfy schema
                if "format" not in spec or not str(spec["format"]).strip():
                    ch = spec.get("channel", "")
                    # If channel contains a hint like "Email - Trial Nurture", reuse right side
                    spec["format"] = ch.split(" - ", 1)[1] if " - " in ch else "N/A"

    return ExecutionPlan.model_validate(data)


# -------------------------------
# Validate Plan (Brief ↔ Plan Alignment)
# -------------------------------
def validate_plan(
    brief: str,
    plan_json: Dict[str, Any],
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    deployment: Optional[str] = None
) -> Dict[str, Any]:
    """
    Compares the original brief vs the generated execution plan and returns:
      - score (1-10)
      - issues (list)
      - suggestions (list)
    """
    client = get_azure_client(api_key, endpoint)
    model_name = deployment or "gpt-5.4-delta"

    if not client:
        return get_mock_validation()

    prompt = f"""
You are a campaign QA analyst.

Compare the campaign brief and the execution plan.
Identify misalignments, missing details, and contradictions.

Return JSON with EXACT keys:
- score (1-10)
- issues (list)
- suggestions (list)

Brief:
{brief}

Execution Plan JSON:
{json.dumps(plan_json, ensure_ascii=False)}
"""

    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    raw = response.choices[0].message.content

    # Safe parse
    try:
        data = json.loads(raw)
    except Exception:
        return get_mock_validation()

    # Normalize to avoid UI crashes
    if not isinstance(data, dict):
        return get_mock_validation()

    score = data.get("score", 7)
    try:
        score = int(score)
    except Exception:
        score = 7
    score = max(1, min(10, score))

    issues = data.get("issues", [])
    suggestions = data.get("suggestions", [])

    if not isinstance(issues, list):
        issues = [str(issues)]
    if not isinstance(suggestions, list):
        suggestions = [str(suggestions)]

    return {
        "score": score,
        "issues": [str(x) for x in issues if str(x).strip()],
        "suggestions": [str(x) for x in suggestions if str(x).strip()]
    }