from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict


# -------------------------------
# STEP 1: Brief Analysis Output
# -------------------------------
class BriefAnalysis(BaseModel):
    campaign_name: Optional[str] = Field(None, description="The name of the campaign")
    objective: Optional[str] = Field(None, description="The main goal of the campaign")
    audience: Optional[str] = Field(None, description="The target audience")
    message: Optional[str] = Field(None, description="The core marketing message")

    channels: List[str] = Field(
        default_factory=list,
        description="Planned marketing channels"
    )

    budget: Optional[str] = Field(None, description="Allocated budget")
    timeline: Optional[str] = Field(None, description="Campaign duration and dates")

    # ✅ Already in your version (kept)
    missing_fields: List[str] = Field(
        default_factory=list,
        description="Fields that are completely missing"
    )

    ambiguities: List[str] = Field(
        default_factory=list,
        description="Fields that are unclear or vague"
    )

    clarification_questions: List[str] = Field(
        default_factory=list,
        description="Specific questions to resolve missing or ambiguous information"
    )


# -------------------------------
# STEP 2: Channel-Level Planning
# -------------------------------
class ChannelSpec(BaseModel):
    channel: str = Field(..., description="Channel name (e.g., Email, LinkedIn)")

    # ✅ Required → prevents earlier crash
    format: str = Field(..., description="Content format (e.g., video, carousel, newsletter)")

    # ✅ High-value additions (kept)
    objective: Optional[str] = Field(None, description="Purpose of this channel in campaign")
    cta: Optional[str] = Field(None, description="Primary call-to-action")

    # ✅ KPI support
    key_metrics: List[str] = Field(
        default_factory=list,
        description="KPIs for this channel"
    )


# -------------------------------
# STEP 3: Timeline Planning
# -------------------------------
class Milestone(BaseModel):
    # ✅ Flexible (handles both week and date cases)
    week: Optional[Union[int, str]] = Field(None, description="Week number or date range")
    date: Optional[str] = None

    activity: Optional[str] = None
    deliverable: Optional[str] = None
    details: Optional[str] = None


# -------------------------------
# STEP 4: Final Execution Plan
# -------------------------------
class ExecutionPlan(BaseModel):
    campaign_summary: Union[str, Dict[str, str]]

    # ✅ WOW FEATURE (ONLY ADDITION YOU NEEDED)
    confidence_score: Optional[str] = Field(
        None,
        description="Campaign quality score from 1 to 10"
    )

    strengths: List[str] = Field(
        default_factory=list,
        description="Top strengths of the campaign plan"
    )

    risks: List[str] = Field(
        default_factory=list,
        description="Potential risks or gaps"
    )

    # ✅ Existing (kept untouched)
    assumptions: List[str] = Field(
        default_factory=list,
        description="Assumptions made where input was missing"
    )

    channel_specifications: List[ChannelSpec]

    milestones: List[Milestone]

    copy_guidance_stubs: List[Union[str, Dict[str, str]]]

    # ✅ Hackathon gold (kept)
    qa_checklist: List[str] = Field(
        default_factory=list,
        description="Pre-launch quality assurance checklist"
    )