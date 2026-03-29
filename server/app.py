"""
FastAPI application for the Expense Tracker Environment.
"""

try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:
    raise ImportError("openenv is required.") from e

try:
    from models import ExpenseAction, ExpenseObservation
    from server.expense_tracker_environment import ExpenseTrackerEnvironment
except ModuleNotFoundError:
    from ..models import ExpenseAction, ExpenseObservation
    from .expense_tracker_environment import ExpenseTrackerEnvironment

app = create_app(
    ExpenseTrackerEnvironment,
    ExpenseAction,
    ExpenseObservation,
    env_name="expense_tracker",
    max_concurrent_envs=10,
)


def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    main(port=args.port)