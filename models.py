from openenv.core.env_server.types import Action, Observation, State
from pydantic import Field
from typing import Optional, List


class ExpenseAction(Action):
    """What the AI can do."""
    
    action_type: str = Field(..., description="Type of action: 'categorize', 'flag_budget', 'suggest_cut'")
    expense_id: int = Field(..., description="ID of the expense to act on")
    category: Optional[str] = Field(None, description="Category: Food, Transport, Entertainment, Shopping, Bills, Other")
    suggestion: Optional[str] = Field(None, description="Suggestion for budget cut")


class ExpenseObservation(Observation):
    """What the AI sees."""
    
    expenses: List[dict] = Field(default_factory=list, description="List of expenses")
    budget_limits: dict = Field(default_factory=dict, description="Budget limits per category")
    current_totals: dict = Field(default_factory=dict, description="Current spending per category")
    message: str = Field(default="", description="Feedback message")
    score: float = Field(default=0.0, description="Current score")


class ExpenseState(State):
    """Episode metadata."""
    
    task_name: str = Field(default="", description="Current task name")
    total_expenses: int = Field(default=0, description="Total number of expenses")
    correctly_handled: int = Field(default=0, description="Number correctly handled")