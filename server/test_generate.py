import json
from agent import generate_documents

idea = "Build a habit tracker web app where users can create habits, check them off daily, and view a history calendar."

for tier in ["novice", "intermediate", "production"]:
    print(f"\n--- Generating for Tier: {tier} ---")
    try:
        result = generate_documents(idea, tier)
        print(json.dumps(result.model_dump(), indent=2))
    except Exception as e:
        print(f"Error: {e}")
