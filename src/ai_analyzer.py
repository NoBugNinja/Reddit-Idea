import json
import asyncio
from typing import List, Dict
from src.prompts import MAP_PROMPT_TEMPLATE, REDUCE_PROMPT_TEMPLATE

class AIAnalyzer:
    def __init__(self, api_key: str = None, base_url: str = None, model_name: str = "gpt-4o-mini", batch_size: int = 10):
        """
        batch_size: The number of Reddit posts to send to the LLM in one chunk
                    during the Map phase.
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self.batch_size = batch_size
        self.client = None
        
        if self.api_key and self.api_key != "MOCK_KEY":
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
                print("[SUCCESS] Real LLM Client Initialized successfully.")
            except ImportError:
                print("[WARNING] openai package is not installed. Run `pip install openai`. Falling back to Mock.")

    def _chunk_data(self, data: List[Dict]) -> List[List[Dict]]:
        return [data[i: i + self.batch_size] for i in range(0, len(data), self.batch_size)]

    async def _call_llm(self, prompt_template: str, input_data: str) -> str:
        """
        Calls an external LLM API if a valid key is provided; otherwise, uses a mock.
        """
        if self.client:
            try:
                response = await self.client.chat.completions.create(
                    model=self.model_name, 
                    messages=[
                        {"role": "system", "content": prompt_template},
                        {"role": "user", "content": input_data}
                    ],
                    temperature=0.7,
                )
                text = response.choices[0].message.content.strip()
                # Llama 3 models sometimes wrap JSON in markdown blocks or conversational text.
                # Let's forcefully extract the JSON array boundaries:
                start_idx = text.find('[')
                end_idx = text.rfind(']')
                
                if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
                    return text[start_idx:end_idx+1]
                
                return text
            except Exception as e:
                print(f"[ERROR] API Error: {e}")
                return "[]"
                
        # --- MOCK LOGIC BELOW ---
        # print("Mocking LLM call for map/reduce...")
        await asyncio.sleep(0.5) # Simulate network delay
        
        # Simulate an LLM returning some static structured JSON based on prompt
        if "Batch Information" in prompt_template:
            # It's a Map task
            mock_output = [
                {
                    "problem_category": "Workflow Tools",
                    "description": "Users are finding it hard to connect disparate data pipelines automatically.",
                    "evidence_quote": "Is there a tool that just does this easily?",
                    "source_ids": ["mock_123"]
                }
            ]
            return json.dumps(mock_output)
        else:
            # It's a Reduce task
            mock_output = [
                {
                    "problem_category": "Workflow Tools",
                    "description": "Difficulty automating and logging pipeline executions.",
                    "frequency": 15,
                    "severity_evidence": "Many posts complaining about 'struggling with scalable data pipelines'.",
                    "suggested_product_idea": "A unified GUI-based no-code data orchestration tool tailored for startups."
                }
            ]
            return json.dumps(mock_output)

    async def map_phase(self, cleaned_documents: List[Dict]) -> List[Dict]:
        """
        Processes chunks of data to extract intermediate problems.
        """
        chunks = self._chunk_data(cleaned_documents)
        tasks = []
        
        for chunk in chunks:
            # Prepare formatted JSON string of the batch for the prompt
            batch_str = json.dumps([{k: v for k, v in doc.items() if k != "score"} for doc in chunk])
            prompt = MAP_PROMPT_TEMPLATE.replace("{batch_data}", batch_str)
            tasks.append(self._call_llm(prompt, ""))

        print(f"Executing MAP phase across {len(tasks)} batches...")
        
        results = []
        for index, task in enumerate(tasks):
            print(f"  -> Processing batch {index + 1}/{len(tasks)}...")
            res = await task
            results.append(res)
            # Add a delay between batches to respect free-tier API rate limits (like Groq limits)
            if index < len(tasks) - 1:
                await asyncio.sleep(5)

        all_mapped_problems = []
        for res_str in results:
            try:
               parsed = json.loads(res_str)
               if isinstance(parsed, list):
                   all_mapped_problems.extend(parsed)
            except json.JSONDecodeError:
                print("Error parsing LLM response in Map phase. Skipping chunk.")
                continue

        return all_mapped_problems

    async def reduce_phase(self, mapped_problems: List[Dict]) -> List[Dict]:
        """
        Summarizes and aggregates all the problems extracted during the Map phase.
        """
        # If there are massively huge mapped_problems lists, we might need a multi-level reduce.
        # But for this system, we do a single reduce.
        
        problems_str = json.dumps(mapped_problems)
        prompt = REDUCE_PROMPT_TEMPLATE.replace("{aggregated_problems}", problems_str)

        print("Executing REDUCE phase (Aggregating insights)...")
        res_str = await self._call_llm(prompt, "")
        
        try:
             insights = json.loads(res_str)
             return insights if isinstance(insights, list) else []
        except json.JSONDecodeError:
             print("Error parsing LLM response in Reduce phase. Returning empty.")
             return []

    async def run_pipeline(self, documents: List[Dict]) -> List[Dict]:
        """
        End-to-end execution of Map-Reduce problem discovery.
        """
        if not documents:
            return []
        
        intermediate_problems = await self.map_phase(documents)
        final_insights = await self.reduce_phase(intermediate_problems)
        
        return final_insights
