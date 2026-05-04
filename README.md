# 🚀 Marketing Campaign Planner

A powerful AI-driven tool built with Streamlit and OpenAI to help marketing teams transform raw campaign briefs into comprehensive, actionable execution plans.

## ✨ Features

- **Brief Analysis**: Automatically identifies ambiguities and missing information in your campaign brief.
- **Interactive Clarification**: Prompts users for specific details to ensure the AI has all necessary context.
- **Comprehensive Execution Plans**: Generates detailed plans including:
  - Confidence scores and risk assessment.
  - Channel-specific specifications (Format, CTA, Objectives).
  - Milestone timelines with KPIs.
  - Creative copy guidance.
  - QA Checklists.
- **Plan Validation**: Validates the generated plan against the original brief for alignment and consistency.
- **Sample Briefs**: Includes pre-loaded examples to get started quickly.

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **AI Engine**: [OpenAI GPT Models](https://openai.com/)
- **Data Validation**: [Pydantic](https://docs.pydantic.dev/)
- **Environment Management**: `python-dotenv`

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- An OpenAI API Key

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/LatentView-Analytics-Ltd/Felix_Josekannai.git
   cd campaign-planner
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory and add your Azure OpenAI credentials:
   ```env
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
   ```

### Running the App

```bash
streamlit run app.py
```

## 📖 Usage

1. **Input**: Paste your campaign brief or select a sample from the sidebar.
2. **Clarify**: Answer any clarification questions identified by the AI.
3. **Generate**: Review the generated execution plan, timeline, and channel specs.
4. **Validate**: Run the validation step to ensure the plan aligns perfectly with your original goals.

## 📁 Project Structure

- `app.py`: Main Streamlit application and UI logic.
- `llm_utils.py`: Integration logic with OpenAI for analysis and generation.
- `schema.py`: Pydantic models for structured AI outputs.
- `samples.py`: Pre-defined sample campaign briefs.
- `requirements.txt`: Project dependencies.
