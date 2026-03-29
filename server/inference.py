"""
Inference script for Expense Tracker Environment.
Runs a baseline agent against all 3 tasks.
"""

import os
import json
from server.expense_tracker_environment import ExpenseTrackerEnvironment
from models import ExpenseAction


def run_inference():
    env = ExpenseTrackerEnvironment()
    results = {}

    # Easy Task
    obs = env.reset(task="easy")
    total_reward = 0
    steps = 0
    CATEGORY_RULES = {
        "swiggy": "Food", "zomato": "Food", "grocery": "Food",
        "uber": "Transport", "ola": "Transport", "petrol": "Transport",
        "netflix": "Entertainment", "movie": "Entertainment",
        "electricity": "Bills", "internet": "Bills", "bill": "Bills",
        "amazon": "Shopping", "flipkart": "Shopping", "shopping": "Shopping",
    }
    while not obs.done and steps < 5:
        expense = obs.expenses[steps]
        desc = expense["description"].lower()
        category = "Other"
        for keyword, cat in CATEGORY_RULES.items():
            if keyword in desc:
                category = cat
                break
        action = ExpenseAction(action_type="categorize", expense_id=expense["id"], category=category)
        obs = env.step(action)
        total_reward += obs.reward or 0
        steps += 1
    results["easy"] = round(total_reward / max(steps, 1), 2)

    # Medium Task
    obs = env.reset(task="medium")
    total_reward = 0
    steps = 0
    while not obs.done and steps < 5:
        expense = obs.expenses[steps]
        category = expense.get("category", "Other")
        action = ExpenseAction(action_type="flag_budget", expense_id=expense["id"], category=category)
        obs = env.step(action)
        total_reward += obs.reward or 0
        steps += 1
    results["medium"] = round(total_reward / max(steps, 1), 2)

    # Hard Task
    obs = env.reset(task="hard")
    total_reward = 0
    steps = 0
    sorted_expenses = sorted(obs.expenses, key=lambda x: x["amount"], reverse=True)
    while not obs.done and steps < 8:
        expense = sorted_expenses[steps]
        action = ExpenseAction(
            action_type="suggest_cut",
            expense_id=expense["id"],
            suggestion=f"Reduce {expense['description']} by 30%"
        )
        obs = env.step(action)
        total_reward += obs.reward or 0
        steps += 1
    results["hard"] = round(total_reward / max(steps, 1), 2)

    results["overall"] = round(sum(results.values()) / 3, 2)
    
    print(json.dumps(results, indent=2))
    return results


if __name__ == "__main__":
    run_inference()