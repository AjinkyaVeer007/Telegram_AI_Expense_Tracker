from tracker.agent import app
from tracker.agent.state import initial_state
from tracker.config import setup_logging
from tracker.formatting import format_result


def main() -> None:
    setup_logging()
    print("AI EXPENSE TRACKER (type 'exit' to quit)")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break
        if not user_input:
            continue

        result = app.invoke(initial_state(user_input))
        print(f"\nBot: {format_result(result)}")


if __name__ == "__main__":
    main()
