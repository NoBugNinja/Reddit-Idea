MAP_PROMPT_TEMPLATE = """
You are an expert AI product researcher analyzing raw Reddit posts.
Your goal is to extract real-world problems and unmet needs from the user complaints below.

Please analyze the following batch of Reddit posts and extract structured problem statements.
Disregard any rants that are purely emotional without a specific practical problem.

Batch Information:
{batch_data}

Output Format Guidelines (JSON only):
Return a JSON list of objects, each containing:
- "problem_category": A short, 2-3 word category (e.g., "Data Integration", "B2B Sales").
- "description": A clear description of the problem the user is facing.
- "evidence_quote": A direct quote from the text demonstrating the problem.
- "source_ids": A list containing the ID of the post(s) demonstrating this problem.

Do not include any Markdown wrapping, simply return valid JSON. If no problems are found, return `[]`.
"""

REDUCE_PROMPT_TEMPLATE = """
You are a senior product strategist and AI researcher. 
You are given a list of extracted problems across many different Reddit posts. Your job is to aggregate them, identify the most critical recurring themes, and propose viable startup product ideas based on these pain points.

Extracted Problems:
{aggregated_problems}

Output Guidelines (JSON only):
Return a JSON list of aggregated insights. For each major problem cluster, provide:
- "problem_category": The high-level category representing this cluster.
- "description": A consolidated description of the problem.
- "frequency": The number of times this problem appeared in the input data.
- "severity_evidence": Representative quotes or a summary of why it's painful.
- "suggested_product_idea": A concise startup idea or SaaS tool that solves this exact problem in a scalable way.

Do not include any Markdown wrapping, return strictly valid JSON.
"""
