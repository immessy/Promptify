import json
from agent import classify_idea

ideas = [
    "Write a quick python script to parse a csv file and print the total sales column.", # expected novice
    "Build a habit tracker web app where users can create habits, check them off daily, and view a history calendar.", # expected intermediate or production depending on users/auth
    "Create a fully scalable multi-tenant SaaS for managing hospital patient records, with secure auth, audit logs, and a dashboard." # expected production
]

for idea in ideas:
    print(f"\n--- Idea: {idea} ---")
    try:
        result = classify_idea(idea)
        print(json.dumps(result.model_dump(), indent=2))
    except Exception as e:
        print(f"Error: {e}")
