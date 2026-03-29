import json
from server.expense_tracker_environment import ExpenseTrackerEnvironment
from models import ExpenseAction

def run_inference():
    env = ExpenseTrackerEnvironment()
    results = {}
    obs = env.reset(task="easy")
    total_reward = 0
    steps = 0
    while not obs.done and steps < 5:
        expense = obs.expenses[steps]
        desc = expense["description"].lower()
        category = "Food" if any(k in desc for k in ["swiggy","grocery","zomato"]) else "Transport" if any(k in desc for k in ["uber","ola"]) else "Entertainment" if "netflix" in desc else "Bills" if "electricity" in desc else "Shopping" if "shopping" in desc else "Other"
        action = ExpenseAction(action_type="categorize", expense_id=expense["id"], category=category)
        obs = env.step(action)
        total_reward += obs.reward or 0
        steps += 1
    results["easy"] = round(total_reward / max(steps, 1), 2)
    obs = env.reset(task="medium")
    total_reward = 0
    steps = 0
    while not obs.done and steps < 5:
        expense = obs.expenses[steps]
        action = ExpenseAction(action_type="flag_budget", expense_id=expense["id"], category=expense.get("category","Other"))
        obs = env.step(action)
        total_reward += obs.reward or 0
        steps += 1
    results["medium"] = round(total_reward / max(steps, 1), 2)
    obs = env.reset(task="hard")
    total_reward = 0
    steps = 0
    sorted_exp = sorted(obs.expenses, key=lambda x: x["amount"], reverse=True)
    while not obs.done and steps < 8:
        expense = sorted_exp[steps]
        action = ExpenseAction(action_type="suggest_cut", expense_id=expense["id"], suggestion="Reduce by 30%")
        obs = env.step(action)
        total_reward += obs.reward or 0
        steps += 1
    results["hard"] = round(total_reward / max(steps, 1), 2)
    results["overall"] = round(sum(results.values()) / 3, 2)
    print(json.dumps(results, indent=2))
    return results

if __name__ == "__main__":
    run_inference()
