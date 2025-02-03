from langchain_openai import ChatOpenAI
from langchain_google_vertexai import VertexAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import dotenv
import random

# Load environment variables
dotenv.load_dotenv()

# Unified Instructions
instructions = """
Welcome to the AI Model Challenge Game!

Game Overview:
- Three AI models (ChatGPT, Gemini, Deepseek) will compete in multiple rounds.
- Each round consists of role rotations: Asker, Responder, and Judge.

Roles:
1. Asker: Generates a deterministic, factual, and verifiable question.
2. Responder: Attempts to answer the question accurately.
3. Judge: Evaluates the correctness of the response and the determinism of the question.

Scoring:
- Correct answer: Responder gains 1 point.
- Incorrect answer: Asker gains 1 point.
- Non-deterministic question (after 3 attempts): Asker loses 0.5 points.

Rules:
- Questions should focus on math, physics, and historical facts with fixed values.
- Avoid subjective, ambiguous, or data-sensitive questions.
- Each round includes two questions (one from each Asker).

Let the challenge begin!
"""

# Define AI models as agents with names
agent_chatgpt = ChatOpenAI(model_name="gpt-4o-mini", temperature=1)
agent_chatgpt.name = "ChatGPT"

agent_gemini = VertexAI(model_name="gemini-2.0-flash-exp")
agent_gemini.name = "Gemini"

agent_deepseek = ChatOpenAI(model_name="gpt-4o-mini", temperature=1)  # Placeholder for Deepseek equivalent
agent_deepseek.name = "Deepseek"

ai_models = [agent_chatgpt, agent_gemini, agent_deepseek]

# Initialize scores and question history
scores = {"ChatGPT": 0, "Gemini": 0, "Deepseek": 0}
question_history = []

# Helper function to extract content safely
def extract_content(response):
    if isinstance(response, AIMessage):
        return response.content
    return str(response)

# Mock functions for agent behavior

def generate_question(agent):
    challenge = (
        "Create a challenging question that is strictly deterministic, factual, and verifiable. "
        "It should have only one correct answer based on objective facts such as numerical, historical, or scientific data. "
        "Avoid subjective, ambiguous, or data-sensitive questions. Focus on math, physics, and historical facts with fixed values."
    )
    messages = [SystemMessage(content=challenge)]
    response = agent.invoke(messages)
    question = extract_content(response)

    # Check for duplicate questions or similar keywords
    if question in question_history:
        return generate_question(agent)

    question_history.append(question)
    return question


def validate_question_determinism(judge, question):
    checklist = (
        "Evaluate if the question is deterministic using the following criteria:\n"
        "1. Is the question based on objective facts?\n"
        "2. Can it be answered without subjective judgment?\n"
        "3. Does the answer remain the same regardless of interpretation?\n"
        "Provide a confidence score from 0 to 10, where 10 means highly deterministic and 0 means completely non-deterministic."
        "Respond with a number between 0 and 10, and no additional text."
    )
    messages = [
        SystemMessage(content=f"{checklist}\nQuestion: '{question}'")
    ]
    response = judge.invoke(messages)
    try:
        confidence_score = int(extract_content(response).strip())
        return confidence_score >= 7  # Threshold to allow the question
    except ValueError:
        print("Invalid confidence score. Assuming non-deterministic question.")
        return False


def respond_to_question(agent, question):
    if not isinstance(question, str):  # Ensure question is a string
        question = str(question)
    messages = [HumanMessage(content=question)]
    response = agent.invoke(messages)
    return extract_content(response)  # Ensure the response is a string


def evaluate_answer(agent, question, answer):
    messages = [
        SystemMessage(
            content=f"Evaluate if the answer '{answer}' to the question '{question}' is correct. Reply with 'correct' or 'incorrect'."
        )
    ]
    response = agent.invoke(messages)
    return extract_content(response).strip().lower()


def make_judgment(agent, question, answer, asker_opinion):
    messages = [
        SystemMessage(
            content=f"The asker says the answer '{answer}' to the question '{question}' is '{asker_opinion}'. "
                    f"As a judge, give your final decision: 'correct', 'incorrect', or 'non-deterministic'."
                    f"respond with 'correct', 'incorrect', or 'non-deterministic' without any additional text."
        )
    ]
    response = agent.invoke(messages)
    return extract_content(response).strip().lower()

# Role rotation function
def rotate_roles(round_num, start_index):
    asker1 = ai_models[(start_index + round_num) % 3]
    asker2 = ai_models[(start_index + round_num + 1) % 3]
    judge = ai_models[(start_index + round_num + 2) % 3]
    return asker1, asker2, judge

# Simulate one round
def play_round(round_num, start_index):
    print(f"Round {round_num + 1}:")
    print('*' * 9)
    asker1, asker2, judge = rotate_roles(round_num, start_index)

    # Each asker generates a question
    for asker, responder in [(asker1, asker2), (asker2, asker1)]:
        question = generate_question(asker)

        # Pre-validate determinism before answering
        attempts = 0
        while not validate_question_determinism(judge, question) and attempts < 3:
            print(f"Question from {asker.name} was non-deterministic. Regenerating question...")
            question = generate_question(asker)
            attempts += 1

        if attempts == 3:
            print(f"Failed to generate a deterministic question after 3 attempts. No points awarded.")
            scores[asker.name] -= 1  # Reduced penalty
            continue

        # Responder tries to answer
        answer = respond_to_question(responder, question)

        # Asker provides initial correctness judgment
        asker_opinion = evaluate_answer(asker, question, answer)

        # Judge makes the final call
        final_decision = make_judgment(judge, question, answer, asker_opinion)

        # Update scores
        if final_decision == "correct":
            scores[responder.name] += 1
            result = f"{responder.name} answered correctly."
        elif final_decision == "incorrect":
            scores[asker.name] += 1
            result = f"{responder.name} answered incorrectly."
        else:
            result = f"The question was non-deterministic. No points awarded."
            scores[asker.name] -= 1  # Reduced penalty

        # Print result
        print(f"Question (from {asker.name} to {responder.name}):\n{question}")
        print()
        print(f"Answer (by {responder.name}):\n{answer}")
        print()
        print(f"Final Decision (by {judge.name}): {result}\n")
        print('-' * 9)
        print()

# Run the game
def run_game(rounds=9):
    print(instructions)  # Display instructions before starting the game
    start_index = random.randint(0, 2)  # Randomize the first player
    for round_num in range(rounds):
        play_round(round_num, start_index)

    # Display final scores
    print("\nFinal Scores:")
    for model, score in scores.items():
        print(f"{model}: {score}")

if __name__ == "__main__":
    run_game()
