import streamlit as st
import html

from llm_utils import analyze_brief, generate_execution_plan, validate_plan
from samples import SAMPLE_BRIEFS


st.set_page_config(
    page_title="Marketing Campaign Planner",
    page_icon="🚀",
    layout="wide"
)

# -------------------------------
# Session state
# -------------------------------
if "step" not in st.session_state:
    st.session_state.step = "input"

if "brief" not in st.session_state:
    st.session_state.brief = ""

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "answers" not in st.session_state:
    st.session_state.answers = {}

if "plan" not in st.session_state:
    st.session_state.plan = None

if "validation" not in st.session_state:
    st.session_state.validation = None


# -------------------------------
# MAIN
# -------------------------------
def main():
    st.title("🚀 Marketing Campaign Planner")

    with st.sidebar:
        st.subheader("Sample Briefs")

        selected = st.selectbox(
            "Choose a sample",
            ["None"] + list(SAMPLE_BRIEFS.keys())
        )

        if selected != "None":
            st.session_state.brief = html.unescape(SAMPLE_BRIEFS[selected])
            st.info(f"Loaded: {selected}")

    if st.session_state.step == "input":
        render_input()
    elif st.session_state.step == "clarify":
        render_clarification_stage()
    else:
        render_execution_plan_stage()


# -------------------------------
# STEP 1
# -------------------------------
def render_input():
    st.header("Step 1: Enter Campaign Brief")

    brief = st.text_area(
        "Paste your campaign brief",
        height=300,
        value=st.session_state.brief
    )

    if st.button("Analyze Brief"):
        if brief:
            st.session_state.brief = brief
            st.session_state.analysis = analyze_brief(brief)
            st.session_state.step = "clarify"
            st.rerun()
        else:
            st.warning("Please enter a brief")


# -------------------------------
# STEP 2 (Improved Hints ✅)
# -------------------------------
def render_clarification_stage():
    st.header("Step 2: Clarify Details")

    analysis = st.session_state.analysis
    st.info("💡 Answer key questions — AI fills the rest.")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📌 Summary")
        st.write(f"**Name:** {analysis.campaign_name}")
        st.write(f"**Objective:** {analysis.objective}")
        st.write(f"**Audience:** {analysis.audience}")

    with col2:
        with st.expander("⚠️ Key Ambiguities"):
            for amb in analysis.ambiguities:
                st.warning(amb)

        st.subheader("❓ Questions")

        # ✅ FIXED HINT LOGIC
        def get_hint(q):
            q_lower = q.lower()

            # Budget split
            if "split" in q_lower or "across" in q_lower:
                return "e.g., 50% Instagram, 30% LinkedIn, 20% Email"

            # Budget scope
            elif "include" in q_lower or "production" in q_lower or "media" in q_lower:
                return "e.g., 70% media, 30% creative OR media-only"

            # Total budget
            elif "budget" in q_lower:
                return "e.g., $8000 total"

            # Channels
            elif "social" in q_lower or "channel" in q_lower:
                return "e.g., LinkedIn (paid), Instagram (organic)"

            elif "paid" in q_lower or "organic" in q_lower:
                return "e.g., Instagram paid ads + LinkedIn organic posts"

            # Audience targeting
            elif "target" in q_lower:
                return "e.g., trial users, decision-makers, or both"

            # KPI
            elif "kpi" in q_lower or "metric" in q_lower:
                return "e.g., conversions, CTR, CPA"

            # Timeline
            elif "date" in q_lower or "end date" in q_lower:
                return "e.g., July 15, 2026"

            # Offer
            elif "offer" in q_lower or "incentive" in q_lower:
                return "e.g., 10% discount or free consultation"

            else:
                return "Optional — AI will assume if blank"

        answers = {}

        with st.form("form"):
            for q in analysis.clarification_questions:
                answers[q] = st.text_input(q, placeholder=get_hint(q))

            submit = st.form_submit_button("Generate Plan")

        if submit:
            st.session_state.answers = answers
            st.session_state.plan = generate_execution_plan(
                st.session_state.brief,
                answers
            )
            st.session_state.step = "plan"
            st.session_state.validation = None
            st.rerun()


# -------------------------------
# STEP 3 + STEP 4
# -------------------------------
def render_execution_plan_stage():
    st.header("Step 3: Execution Plan")

    plan = st.session_state.plan

    # ✅ Existing Score
    st.subheader("📈 Campaign Health")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Score", f"{plan.confidence_score} / 10")

    with col2:
        st.write("✅ Strengths")
        for s in plan.strengths:
            st.write(f"- {s}")

    with col3:
        st.write("⚠️ Risks")
        for r in plan.risks:
            st.write(f"- {r}")

    st.subheader("📊 Summary")
    st.write(plan.campaign_summary)

    st.subheader("🧠 Assumptions")
    for a in plan.assumptions:
        st.write(f"- {a}")

    st.subheader("📺 Channels")
    for spec in plan.channel_specifications:
        with st.expander(spec.channel):
            st.write(f"Format: {spec.format}")
            if spec.objective:
                st.write(f"🎯 {spec.objective}")
            if spec.cta:
                st.write(f"👉 CTA: {spec.cta}")

    st.subheader("📅 Timeline")

    timeline = []
    for m in plan.milestones:
        display_time = m.week if getattr(m, "week", None) else getattr(m, "date", None)

        timeline.append({
            "Time": display_time,
            "Activity": m.activity,
            "KPI": m.deliverable if getattr(m, "deliverable", None) else "Track performance"
        })

    st.table(timeline)

    st.subheader("✍️ Copy Guidance")
    for c in plan.copy_guidance_stubs:
        st.write(f"• {c}")

    st.subheader("✅ QA Checklist")
    for q in plan.qa_checklist:
        st.write(f"✔️ {q}")

    with st.expander("🔍 JSON"):
        st.json(plan.model_dump())

    # -------------------------------
    # STEP 4: Validation ✅
    # -------------------------------
    st.divider()
    st.header("Step 4: Validate Plan")

    if st.button("Validate Plan"):
        st.session_state.validation = validate_plan(
            st.session_state.brief,
            plan.model_dump()
        )

    if st.session_state.validation:

        v = st.session_state.validation
        score = v["score"]

        st.subheader("✅ Validation Score")
        st.metric("Alignment Score", f"{score} / 10")

        if score >= 8:
            st.success("✅ Strong alignment with brief")
        elif score >= 5:
            st.warning("⚠️ Moderate alignment — review")
        else:
            st.error("❌ Poor alignment — fix required")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("⚠️ Issues")
            for i in v["issues"]:
                st.warning(i)

        with col2:
            st.subheader("💡 Suggestions")
            for s in v["suggestions"]:
                st.write(f"- {s}")

    if st.button("Restart"):
        st.session_state.step = "input"
        st.session_state.validation = None
        st.rerun()


if __name__ == "__main__":
    main()
