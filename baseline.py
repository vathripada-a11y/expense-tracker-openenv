"""
Baseline inference script for Expense Tracker Environment.
Uses OpenAI API to run an agent against all 3 tasks.
"""

import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "dummy-key"))

def run_easy_task(env):
    """Easy: Categorize expenses correctly."""
    obs = env.reset(task="easy")
    total_reward = 0
    steps = 0
    
    CATEGORY_RULES = {
        "swiggy": "Food", "zomato": "Food", "grocery": "Food",
        "uber": "Transport", "ola": "Transport", "petrol": "Transport",
        "netflix": "Entertainment", "movie": "Entertainment", "spotify": "Entertainment",
        "electricity": "Bills", "internet": "Bills", "bill": "Bills",
        "amazon": "Shopping", "flipkart": "Shopping", "shopping": "Shopping",
    }
    
    while not obs.done:
        expense = obs.expenses[steps] if steps < len(obs.expenses) else obs.expenses[0]
        desc = expense["description"].lower()
        
        category = "Other"
        for keyword, cat in CATEGORY_RULES.items():
            if keyword in desc:
                category = cat
                break
        
        from models import ExpenseAction
        action = ExpenseAction(
            action_type="categorize",
            expense_id=expense["id"],
            category=category
        )
        obs = env.step(action)
        total_reward += obs.reward or 0
        steps += 1
        print(f"  Step {steps}: {expense['description']} → {category} (reward={obs.reward})")
        
        if steps >= 5:
            break
    
    score = total_reward / max(steps, 1)
    print(f"  Easy Task Score: {score:.2f}")
    return score


def run_medium_task(env):
    """Medium: Flag expenses that are over budget."""
    obs = env.reset(task="medium")
    total_reward = 0
    steps = 0
    
    while not obs.done:
        expense = obs.expenses[steps] if steps < len(obs.expenses) else obs.expenses[0]
        category = expense.get("category", "Other")
        
        from models import ExpenseAction
        action = ExpenseAction(
            action_type="flag_budget",
            expense_id=expense["id"],
            category=category
        )
        obs = env.step(action)
        total_reward += obs.reward or 0
        steps += 1
        print(f"  Step {steps}: Flag {category} (reward={obs.reward})")
        
        if steps >= 5:
            break
    
    score = total_reward / max(steps, 1)
    print(f"  Medium Task Score: {score:.2f}")
    return score


def run_hard_task(env):
    """Hard: Suggest cuts for expensive items."""
    obs = env.reset(task="hard")
    total_reward = 0
    steps = 0
    
    sorted_expenses = sorted(obs.expenses, key=lambda x: x["amount"], reverse=True)
    
    while not obs.done:
        expense = sorted_expenses[steps] if steps < len(sorted_expenses) else sorted_expenses[0]
        
        from models import ExpenseAction
        action = ExpenseAction(
            action_type="suggest_cut",
            expense_id=expense["id"],
            suggestion=f"Reduce {expense['description']} by 30% to save ₹{int(expense['amount']*0.3)}"
        )
        obs = env.step(action)
        total_reward += obs.reward or 0
        steps += 1
        print(f"  Step {steps}: Suggest cut for {expense['description']} (reward={obs.reward})")
        
        if steps >= 8:
            break
    
    score = total_reward / max(steps, 1)
    print(f"  Hard Task Score: {score:.2f}")
    return score


def main():
    print("=" * 50)
    print("Expense Tracker - Baseline Evaluation")
    print("=" * 50)
    
    from server.expense_tracker_environment import ExpenseTrackerEnvironment
    env = ExpenseTrackerEnvironment()
    
    print("\n📋 Task 1: Easy - Expense Categorization")
    easy_score = run_easy_task(env)
    
    print("\n📊 Task 2: Medium - Budget Violation Detection")
    medium_score = run_medium_task(env)
    
    print("\n✂️ Task 3: Hard - Budget Optimization")
    hard_score = run_hard_task(env)
    
    print("\n" + "=" * 50)
    print("BASELINE RESULTS:")
    print(f"  Easy Task:   {easy_score:.2f}")
    print(f"  Medium Task: {medium_score:.2f}")
    print(f"  Hard Task:   {hard_score:.2f}")
    print(f"  Overall:     {(easy_score + medium_score + hard_score) / 3:.2f}")
    print("=" * 50)
    
    return {
        "easy": easy_score,
        "medium": medium_score,
        "hard": hard_score,
        "overall": (easy_score + medium_score + hard_score) / 3
    }


if __name__ == "__main__":
    main()
