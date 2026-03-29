# 💰 Expense Tracker Environment

An OpenEnv environment where AI agents learn to manage personal finances — categorizing expenses, detecting budget violations, and optimizing spending.

## Motivation

Every person struggles with tracking where their money goes. This environment trains AI agents to help with the most common personal finance tasks that millions of people face daily.

## Tasks

| Task | Difficulty | Description | Baseline Score |
|------|-----------|-------------|----------------|
| Categorize Expenses | Easy | Assign correct categories to expenses | 1.00 |
| Detect Budget Violations | Medium | Flag categories that exceed budget limits | 0.78 |
| Optimize Budget | Hard | Suggest cuts to stay within total budget | 0.58 |

## Action Space
```json
{
  "action_type": "categorize | flag_budget | suggest_cut",
  "expense_id": 0,
  "category": "Food | Transport | Entertainment | Shopping | Bills | Other",
  "suggestion": "optional suggestion text"
}
```

## Observation Space
```json
{
  "expenses": [{"id": 0, "description": "Swiggy order", "amount": 450, "category": null}],
  "budget_limits": {"Food": 2000, "Transport": 1500},
  "current_totals": {"Food": 3000},
  "message": "Feedback message",
  "score": 0.0
}
```

## Reward Function

| Action | Reward |
|--------|--------|
| Correct categorization | +1.0 |
| Correct budget flag | +1.0 |
| Good cut suggestion | +0.8 |
| Minor cut suggestion | +0.2 |
| Wrong action | -0.1 |

## Setup
```bash
pip install openenv-core fastapi uvicorn
```

## Usage
```bash
# Run server locally
python -m server.app

# Run baseline evaluation
python baseline.py
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /reset | POST | Start new episode |
| /step | POST | Execute action |
| /state | GET | Get current state |
| /health | GET | Health check |

## Baseline Scores
```
Easy Task:   1.00
Medium Task: 0.78
Hard Task:   0.58
Overall:     0.79
```

## Docker
```bash
docker build -t expense-tracker .
docker run -p 8000:8000 expense-tracker
```