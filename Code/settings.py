"""EduAI - Student Success and Retention System settings."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "student_dataset_cleaned.csv"
OUTPUT_FOLDER = ROOT / "outputs"

TARGET_COLUMN = "at_risk"
RANDOM_STATE = 42


def make_output_folder():
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


def main():
    from preparation import load_and_prepare
    from risk_models import run_risk_models
    from performance_trend import run_performance_trend
    from model_evaluation import run_model_evaluation
    from chatbot import RiskChatbot

    print("\nSTUDENT SUCCESS AND RETENTION SYSTEM")

    # Prepare the dataset
    X_train, y_train, X_test, y_test = load_and_prepare()

    print(
        f"Train: {len(X_train):,} | "
        f"Test: {len(X_test):,} | "
        f"Features: {X_train.shape[1]}"
    )

    # Train and evaluate machine learning models
    run_risk_models(X_train, y_train, X_test, y_test)

    # Analyse student performance
    run_performance_trend()

    # Display model evaluation
    run_model_evaluation()

    print(f"\nOutputs: {OUTPUT_FOLDER}")

    # Start interactive chatbot
    bot = RiskChatbot()

    print("\nSTUDENT SUPPORT CHATBOT")
    print("Type 'exit' to stop.")

    while True:
        question = input("\nStudent: ")

        if question.strip().lower() in {"exit", "quit"}:
            print("Chatbot session ended.")
            break

        print("Chatbot:", bot.respond(question))


if __name__ == "__main__":
    main()
