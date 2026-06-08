import asyncio
import json
import os
from dotenv import load_dotenv

from src.collector import RedditDataCollector
from src.preprocessor import DocumentPreprocessor
from src.ai_analyzer import AIAnalyzer

async def main():
    print("=== REDDIT PRODUCT DISCOVERY SYSTEM ===")
    
    # Configuration
    load_dotenv() # Loads variables from .env if it exists
    data_dir = "./data"
    # Target Subreddits (Filtered for suitable problem-focused communities)
    subreddits = [
        "realtors", "agency", "Accounting", "smallbusiness", 
        "sysadmin", "AskEngineers", "SaaS", "startups",
        "Entrepreneur", "productivity", "personalfinance", "careerguidance"
    ]
    posts_per_sub = 50 # Increase to 500+ for massive historical runs
    time_filter = "month" # Can be: day, week, month, year, all
    
    # 1. Initialize Components
    collector = RedditDataCollector(data_dir=data_dir)
    # We lowered the min score/length requirement slightly to catch more startup validation posts
    preprocessor = DocumentPreprocessor(min_score=5, min_length=15)
    
    # Use API key from .env
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL") 
    model_name = os.environ.get("AI_MODEL", "gpt-4o-mini")
    
    analyzer = AIAnalyzer(api_key=api_key, base_url=base_url, model_name=model_name, batch_size=5)

    # 2. Collect Data
    print(f"\n--- PHASE 1: Data Collection (Past {time_filter}) ---")
    raw_posts = await collector.fetch_real_data(subreddits, limit=30, time_filter=time_filter)

    # 3. Preprocess Data
    print("\n--- PHASE 2: Preprocessing & Analytics ---")
    
    # Subreddit volume analytics
    from collections import Counter
    sub_counts = Counter(p.get("subreddit") for p in raw_posts)
    print("Raw Post Volume Scraped by Subreddit:")
    for sub, count in sub_counts.items():
        print(f"  - r/{sub}: {count} posts")
        
    print(f"\nTotal raw documents: {len(raw_posts)}")
    cleaned_posts = preprocessor.filter_and_clean(raw_posts)
    print(f"Total clean documents (filtered for signals/quality/length): {len(cleaned_posts)}")

    # In our mock data, we might have filtered out everything if we are not careful,
    # so we will manually inject some clean posts if empty for demonstration purposes.
    if not cleaned_posts:
        print("Mock preprocessing over-filtered. Injecting a test post for demonstration.")
        cleaned_posts = [{
             "id": "demo_123",
             "subreddit": "startup",
             "text": "I really struggle with building scalable data pipelines. Is there a tool that just does this easily?",
             "score": 15
        }]

    # 4. AI Analysis
    print("\n--- PHASE 3: AI Analysis (Map-Reduce) ---")
    final_insights = await analyzer.run_pipeline(cleaned_posts)

    # 5. Output Generation
    print("\n--- PHASE 4: Final Product Insights ---")
    
    output_file = "startup_insights.json"
    with open(output_file, "w") as f:
        json.dump(final_insights, f, indent=4)
        
    for insight in final_insights:
        print("\n---------------------------------------------------------")
        print(f"CATEGORY: {insight.get('problem_category')}")
        print(f"PROBLEM:  {insight.get('description')}")
        print(f"FREQ:     {insight.get('frequency')} occurrences")
        print(f"EVIDENCE: {insight.get('severity_evidence')}")
        print(f"SUGGESTED PRODUCT IDEA: {insight.get('suggested_product_idea')}")
        print("---------------------------------------------------------")

    print(f"\nProcessing complete. Report saved to {output_file}.")

if __name__ == "__main__":
    asyncio.run(main())
