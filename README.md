# Reddit Product Discovery System

An automated pipeline designed to ingest data from Reddit communities, filter out noise, and leverage Large Language Models (LLMs) to identify real-world problems, repeated complaints, and potential startup opportunities.

## 🚀 Features

- **Data Collection**: Scrapes recent posts from targeted professional and business-focused subreddits.
- **Intelligent Preprocessing**: Heuristic filtering to discard noise, short rants, and low-quality posts while keeping "need statements" and genuine complaints.
- **Map-Reduce AI Analysis**: Overcomes LLM context window limitations by processing data in chunks (Map) and then synthesizing broad insights across the entire dataset (Reduce).
- **Actionable Output**: Generates structured reports containing problem categories, frequency, evidence quotes, and suggested product ideas.

## 📋 Prerequisites

- Python 3.8+
- An OpenAI API Key (or equivalent LLM provider API Key)

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/NoBugNinja/Reddit-Idea.git
   cd Reddit-Idea
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup:**
   Create a `.env` file in the root directory and add your API credentials:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   AI_MODEL=gpt-4o-mini  # Optional: change model if needed
   ```

## 🚀 Usage

Run the main pipeline script to start the data collection, preprocessing, and AI analysis process:

```bash
python main_pipeline.py
```

The system will output progress to the console and save the final report to `startup_insights.json`.

## 🏗️ Architecture

For a deep dive into how the system works, data flows, and scaling recommendations, please see the [System Architecture Document](system_architecture.md).

## 📄 Output Example

The resulting `startup_insights.json` will contain structured data similar to:

```json
{
  "problem_category": "Data Engineering",
  "description": "Users struggle with building and maintaining scalable data pipelines without extensive DevOps knowledge.",
  "frequency": 15,
  "severity_evidence": "I really struggle with building scalable data pipelines. Is there a tool that just does this easily?",
  "suggested_product_idea": "A low-code drag-and-drop data pipeline builder with automated infrastructure provisioning."
}
```