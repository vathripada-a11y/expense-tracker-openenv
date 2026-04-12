import json
import requests
import sys

def get_base_url():
    for url in ["http://localhost:7860", "http://localhost:8000", "https://thripada-expense-tracker.hf.space"]:
        try:
            r = requests.get(f"{url}/health", timeout=10)
            if r.status_code == 200:
                return url
        except:
            continue
    return "https://thripada-expense-tracker.hf.space"

BASE_URL = get_base_url()
print(f"Using: {BASE_URL}")

def reset(task="easy"):
    r = requests.post(f"{BASE_URL}/reset", json={"episode_id": task}, timeout=30)
    return r.json()

def step(action_data):
    r = requests.post(f"{BASE_URL}/step", json={"action": action_data}, timeout=30)
    return r.json()

def run_inference():
    results = {}

    try:
        obs = reset("easy")
        total_reward = 0
        steps = 0
        RULES = {"swiggy": "Food", "zomato": "Food", "grocery": "Food", "uber": "Transport", "ola": "Transport", "netflix": "Entertainment", "electricity": "Bills", "bill": "Bills", "shopping": "Shopping"}
        expenses = obs.get("observation", {}).get("expenses", [])
        for i in range(min(5, len(expenses))):
            expense = expenses[i]
            desc = expense["description"].lower()
            category = next((cat for kw, cat in RULES.items() if kw in desc), "Other")
            result = step({"action_type": "categorize", "expense_id": expense["id"], "category": category})
            total_reward += result.get("reward") or 0
            steps += 1
        results["easy"] = round(total_reward / max(steps, 1), 2)
    except Exception as e:
        print(f"Easy error: {e}")
        results["easy"] = 0.0

    try:
        obs = reset("medium")
        total_reward = 0
        steps = 0
        expenses = obs.get("observation", {}).get("expenses", [])
        for i in range(min(5, len(expenses))):
            expense = expenses[i]
            result = step({"action_type": "flag_budget", "expense_id": expense["id"], "category": expense.get("category", "Other")})
            total_reward += result.get("reward") or 0
            steps += 1
        results["medium"] = round(total_reward / max(steps, 1), 2)
    except Exception as e:
        print(f"Medium error: {e}")
        results["medium"] = 0.0

    try:
        obs = reset("hard")
        total_reward = 0
        steps = 0
        expenses = sorted(obs.get("observation", {}).get("expenses", []), key=lambda x: x["amount"], reverse=True)
        for i in range(min(8, len(expenses))):
            result = step({"action_type": "suggest_cut", "expense_id": expenses[i]["id"], "suggestion": "Reduce by 30%"})
            total_reward += result.get("reward") or 0
            steps += 1
        results["hard"] = round(total_reward / max(steps, 1), 2)
    except Exception as e:
        print(f"Hard error: {e}")
        results["hard"] = 0.0

    results["overall"] = round(sum(results.values()) / 3, 2)
    print(json.dumps(results, indent=2))
    return results

if _name_ == "_main_":
    run_inference()
