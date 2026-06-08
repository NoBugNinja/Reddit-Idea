import asyncio
import json
from src.collector import RedditDataCollector
from src.preprocessor import DocumentPreprocessor

async def main():
    subreddits = [
        "realtors", "agency", "Accounting", "smallbusiness", 
        "sysadmin", "AskEngineers", "SaaS", "startups",
        "Entrepreneur", "productivity", "personalfinance", "careerguidance"
    ]
    collector = RedditDataCollector(data_dir="./data")
    # Lowered min_score to 1 to catch niche B2B complaints
    preprocessor = DocumentPreprocessor(min_score=1, min_length=15) 
    
    print("Fetching massive dataset...")
    raw_posts = await collector.fetch_real_data(subreddits, limit=150, time_filter="year")
    cleaned_posts = preprocessor.filter_and_clean(raw_posts)
    
    with open("hijacked_data_v2.json", "w") as f:
        json.dump(cleaned_posts, f, indent=2)
        
    print(f"Hijacked {len(cleaned_posts)} posts and saved to hijacked_data.json")

if __name__ == "__main__":
    asyncio.run(main())
