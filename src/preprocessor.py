import re
from typing import List, Dict

class DocumentPreprocessor:
    def __init__(self, min_score: int = 2, min_length: int = 15):
        self.min_score = min_score
        self.min_length = min_length
        # Regex to detect phrases commonly associated with problems/pain points
        self.problem_keywords = re.compile(
            r"(i wish|how do you|struggling with|hate when|is there a tool|hard to|pain point|annoying|frustrated)",
            re.IGNORECASE
        )
        self.seen_ids = set()

    def filter_and_clean(self, raw_documents: List[Dict]) -> List[Dict]:
        """
        Applies cleaning, deduplication, and heuristic filtering.
        """
        cleaned_docs = []

        for doc in raw_documents:
            # 1. Deduplicate by ID
            doc_id = doc.get("id")
            if not doc_id or doc_id in self.seen_ids:
                continue
            
            # 2. Filter Spam/Removed
            text = doc.get("selftext", "").strip()
            if text in ["[removed]", "[deleted]"] or not doc.get("is_robot_indexable", True):
                continue

            # 3. Minimum Quality Filter
            if doc.get("score", 0) < self.min_score:
                continue

            # 4. Length Filter
            combined_text = f"{doc.get('title', '')}\n\n{text}".strip()
            words = combined_text.split()
            if len(words) < self.min_length:
                continue

            # 5. Signal Filter (Heuristic)
            # We want posts with complaining/problem signals.
            if not self.problem_keywords.search(combined_text):
                continue
            
            self.seen_ids.add(doc_id)
            cleaned_docs.append({
                "id": doc_id,
                "subreddit": doc.get("subreddit"),
                "text": combined_text,
                "score": doc.get("score")
            })

        return cleaned_docs
