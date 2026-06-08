import json
import os
import argparse
from typing import List, Dict
import aiohttp
import asyncio

# Example of working with a Pushshift dump or local JSON file, 
# and now direct JSON fetching to bypass API key requirements.

class RedditDataCollector:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    async def fetch_real_data(self, subreddits: List[str], limit: int = 100, time_filter: str = "month") -> List[Dict]:
        """
        Fetches live data directly from Reddit's public JSON endpoints using aiohttp.
        This completely bypasses the need for Developer API Keys or asyncpraw!
        """
        # Using a proper bot user-agent often prevents Reddit's 403 blocks better than faking Chrome
        user_agent = "python:product_discovery_bot:v1.0 (script testing)"
        headers = {'User-Agent': user_agent}
        
        extracted_data = []
        
        async with aiohttp.ClientSession(headers=headers) as session:
            for sub_name in subreddits:
                print(f"[FETCHING] Top {limit} posts from r/{sub_name} (past {time_filter}) publicly...")
                url = f"https://www.reddit.com/r/{sub_name}/top.json?t={time_filter}&limit={limit}"
                
                try:
                    async with session.get(url) as response:
                        if response.status != 200:
                            print(f"[WARNING] Failed to fetch r/{sub_name}. HTTP {response.status}")
                            continue
                            
                        data = await response.json()
                        posts = data.get('data', {}).get('children', [])
                        
                        for post in posts:
                            post_data = post['data']
                            if not post_data.get('is_self'): continue # Skip link/image posts
                            
                            extracted_data.append({
                                "id": post_data.get('id'),
                                "subreddit": sub_name,
                                "title": post_data.get('title', ''),
                                "selftext": post_data.get('selftext', ''),
                                "score": post_data.get('score', 0),
                                "is_robot_indexable": True,
                                "num_comments": post_data.get('num_comments', 0)
                            })
                            
                    # Sleep to respect Reddit's public rate limiting and avoid 403s
                    await asyncio.sleep(4.0)
                except Exception as e:
                    print(f"[ERROR] Error fetching r/{sub_name}: {e}")

        print(f"[SUCCESS] Successfully fetched {len(extracted_data)} live posts total without API keys!")
        return extracted_data

    def process_bulk_file(self, file_path: str, target_subreddits: List[str]) -> List[Dict]:
        """
        Reads a JSON Lines file (typical for Pushshift datasets).
        Returns a list of extracted dictionaries.
        """
        extracted_data = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        if record.get("subreddit") in target_subreddits:
                            extracted_data.append({
                                "id": record.get("id"),
                                "subreddit": record.get("subreddit"),
                                "title": record.get("title", ""),
                                "selftext": record.get("selftext", ""),
                                "score": record.get("score", 0),
                                "is_robot_indexable": record.get("is_robot_indexable", True)
                            })
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            print(f"File {file_path} not found. Skipping.")
            return []
            
        print(f"Extracted {len(extracted_data)} relevant posts from bulk file.")
        return extracted_data

if __name__ == "__main__":
    collector = RedditDataCollector(data_dir="./data")
    mock_files = asyncio.run(collector.fetch_real_data(["startup", "SaaS"]))
    # Example logic: collector.process_bulk_file("RS_2023-01.jsonl", ["programming", "startup"])
