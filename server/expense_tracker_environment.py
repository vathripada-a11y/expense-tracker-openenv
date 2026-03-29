from uuid import uuid4
from typing import Optional
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import ExpenseAction, ExpenseObservation, ExpenseState
except ImportError:
    from models import ExpenseAction, ExpenseObservation, ExpenseState

# Sample expenses for each task
EASY_EXPENSES = [
    {"id": 0, "description": "Swiggy order", "amount": 450, "category": None},
    {"id": 1, "description": "Uber ride", "amount": 200, "category": None},
    {"id": 2, "description": "Netflix subscription", "amount": 649, "category": None},
    {"id": 3, "description": "Electricity bill", "amount": 1200, "category": None},
    {"id": 4, "description": "Grocery shopping", "amount": 800, "category": None},
]

CORRECT_CATEGORIES = {
    0: "Food",
    1: "Transport",
    2: "Entertainment",
    3: "Bills",
    4: "Food",
}

MEDIUM_EXPENSES = [
    {"id": 0, "description": "Swiggy", "amount": 3000, "category": "Food"},
    {"id": 1, "description": "Uber", "amount": 2000, "category": "Transport"},
    {"id": 2, "description": "Movies", "amount": 4000, "category": "Entertainment"},
    {"id": 3, "description": "Shopping", "amount": 6000, "category": "Shopping"},
    {"id": 4, "description": "Bills", "amount": 2000, "category": "Bills"},
]

MEDIUM_BUDGETS = {
    "Food": 2000,
    "Transport": 1500,
    "Entertainment": 2000,
    "Shopping": 3000,
    "Bills": 2500,
}

HARD_EXPENSES = [
    {"id": 0, "description": "Zomato", "amount": 5000, "category": "Food"},
    {"id": 1, "description": "Ola/Uber", "amount": 4000, "category": "Transport"},
    {"id": 2, "description": "OTT platforms", "amount": 3000, "category": "Entertainment"},
    {"id": 3, "description": "Amazon shopping", "amount": 8000, "category": "Shopping"},
    {"id": 4, "description": "Electricity+Internet", "amount": 3500, "category": "Bills"},
    {"id": 5, "description": "Gym membership", "amount": 2000, "category": "Entertainment"},
    {"id": 6, "description": "Restaurant dining", "amount": 4000, "category": "Food"},
    {"id": 7, "description": "Petrol", "amount": 3000, "category": "Transport"},
]

HARD_BUDGET = 20000  # Total monthly budget


class ExpenseTrackerEnvironment(Environment):
    """
    Personal Expense Tracker Environment.
    AI agent learns to categorize expenses, detect budget violations,
    and suggest optimizations.
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._task = "easy"
        self._expenses = []
        self._budget_limits = {}
        self._correctly_handled = 0
        self._total_actions = 0
        self._flags_raised = []
        self._suggestions = []

    def reset(self, task: str = "easy") -> ExpenseObservation:
        """Start a new episode."""
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._task = task
        self._correctly_handled = 0
        self._total_actions = 0
        self._flags_raised = []
        self._suggestions = []

        if task == "easy":
            self._expenses = [e.copy() for e in EASY_EXPENSES]
            self._budget_limits = {}
            message = "Categorize each expense correctly! Categories: Food, Transport, Entertainment, Shopping, Bills, Other"

        elif task == "medium":
            self._expenses = [e.copy() for e in MEDIUM_EXPENSES]
            self._budget_limits = MEDIUM_BUDGETS.copy()
            message = "Detect which categories are over budget and flag them!"

        else:  # hard
            self._expenses = [e.copy() for e in HARD_EXPENSES]
            self._budget_limits = {"total": HARD_BUDGET}
            message = "Suggest cuts to bring total spending within budget!"

        return ExpenseObservation(
            done=False,
            reward=0.0,
            expenses=self._expenses,
            budget_limits=self._budget_limits,
            current_totals=self._calculate_totals(),
            message=message,
            score=0.0,
        )

    def step(self, action: ExpenseAction) -> ExpenseObservation:
        """Process an action."""
        self._state.step_count += 1
        self._total_actions += 1
        reward = 0.0
        message = ""

        if action.action_type == "categorize":
            # Easy task
            correct = CORRECT_CATEGORIES.get(action.expense_id)
            if action.category == correct:
                reward = 1.0
                self._correctly_handled += 1
                message = f"✅ Correct! Expense {action.expense_id} is '{correct}'"
            else:
                reward = -0.1
                message = f"❌ Wrong! '{action.category}' is incorrect for expense {action.expense_id}"

            # Update expense category
            for exp in self._expenses:
                if exp["id"] == action.expense_id:
                    exp["category"] = action.category

        elif action.action_type == "flag_budget":
            # Medium task
            totals = self._calculate_totals()
            flagged_category = None
            for exp in self._expenses:
                if exp["id"] == action.expense_id:
                    flagged_category = exp["category"]

            if flagged_category:
                limit = self._budget_limits.get(flagged_category, 0)
                total = totals.get(flagged_category, 0)
                if total > limit:
                    reward = 1.0
                    self._correctly_handled += 1
                    self._flags_raised.append(action.expense_id)
                    message = f"✅ Correct! {flagged_category} is over budget (₹{total} > ₹{limit})"
                else:
                    reward = -0.1
                    message = f"❌ Wrong! {flagged_category} is within budget (₹{total} <= ₹{limit})"

        elif action.action_type == "suggest_cut":
            # Hard task
            total = sum(e["amount"] for e in self._expenses)
            if action.suggestion:
                self._suggestions.append(action.suggestion)
                # Reward for suggesting cuts on highest expenses
                for exp in self._expenses:
                    if exp["id"] == action.expense_id:
                        if exp["amount"] > 3000:
                            reward = 0.8
                            self._correctly_handled += 1
                            message = f"✅ Good suggestion for expense {action.expense_id} (₹{exp['amount']})"
                        else:
                            reward = 0.2
                            message = f"⚠️ Better to focus on higher expenses first"

        # Check if done
        done = self._total_actions >= len(self._expenses)
        score = self._correctly_handled / max(len(self._expenses), 1)

        return ExpenseObservation(
            done=done,
            reward=reward,
            expenses=self._expenses,
            budget_limits=self._budget_limits,
            current_totals=self._calculate_totals(),
            message=message,
            score=score,
        )

    def _calculate_totals(self) -> dict:
        """Calculate total spending per category."""
        totals = {}
        for exp in self._expenses:
            cat = exp.get("category", "Uncategorized")
            if cat:
                totals[cat] = totals.get(cat, 0) + exp["amount"]
        return totals

    @property
    def state(self) -> State:
        return self._state