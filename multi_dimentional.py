from langchain_openai import ChatOpenAI
from langchain_google_vertexai import VertexAI
from langchain_core.messages import HumanMessage, SystemMessage
import dotenv
import random

dotenv.load_dotenv()

# Unified Instructions
instructions = """
AI Competition Ring Instructions

You are participating in an AI Competition Ring where you will take on three different roles in rotation:

Asker: Create a challenging question with a deterministic (clear-cut) answer, aiming to make the Responder fail. The question should be factual, verifiable, and not open to multiple interpretations. Avoid questions that are ambiguous or subjective.
Responder: Attempt to answer the question accurately using reasoning and available knowledge.
Judge: Evaluate both questions and answers in each round (as there will be two per round). Consider the Asker's opinion but make an independent and final judgment on whether each answer is correct. Additionally, determine if the question itself is deterministic:
If the question is deterministic, assess if the answer is correct or incorrect.
If the question is non-deterministic (ambiguous, subjective, or without a clear-cut answer), declare it as such, and no points will be awarded for that question.

Gameplay Structure:

In each round, both Askers (two AI models) will ask one question each, directed at the other.
The Judge remains the same for both questions in the round and only rotates after both have been judged.

Scoring:
For each answer, evaluate the following dimensions:
- Accuracy: Was the answer factually correct? (0-10)
- Reasoning: Was the reasoning clear, logical, and coherent? (0-10)
- Efficiency: Was the answer concise and to the point? (0-10)
- Adaptability: Did the model handle unfamiliar concepts effectively? (0-10)

Points are awarded based on the sum of these scores for each answer.

Penalty:
If a question is deemed non-deterministic, the Asker loses 0.5 points as a penalty.

Bonus:
If a responder provides an exceptionally insightful answer, the Judge may award a bonus point for "Insightfulness."

Guidelines:
- Ensure fairness and objectivity in questions and judgments.
- Avoid ambiguous, subjective, or unsolvable questions.
- Be concise and clear in your responses and evaluations.
- Your goal is to maximize your score over multiple rounds.
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
scores = {"ChatGPT": {"accuracy": 0, "reasoning": 0, "efficiency": 0, "adaptability": 0, "insightfulness": 0},
          "Gemini": {"accuracy": 0, "reasoning": 0, "efficiency": 0, "adaptability": 0, "insightfulness": 0},
          "Deepseek": {"accuracy": 0, "reasoning": 0, "efficiency": 0, "adaptability": 0, "insightfulness": 0}}

question_history = []

# Mock functions for agent behavior

def generate_question(agent):
    challenge = (
        "Create a challenging question that is strictly deterministic, factual, and verifiable. "
        "It should have only one correct answer based on objective facts such as numerical, historical, or scientific data. "
        "Avoid subjective, ambiguous, or data-sensitive questions. Focus on math, physics, and historical facts with fixed values."
        "Don't provide the answer to the question, or any other information."
    )
    messages = [SystemMessage(content=challenge)]
    response = agent.invoke(messages)
    response = response.content if hasattr(response, 'content') else response
    question = str(response)

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
        "Provide a confidence score from 0 to 10, where 10 means highly deterministic and 0 means completely non-deterministic.\n"
        "Respond with a number between 0 and 10, and no additional text."
    )
    messages = [
        SystemMessage(content=f"{checklist}\nQuestion: '{question}'")
    ]
    response = judge.invoke(messages)
    response = response.content if hasattr(response, 'content') else response

    try:
        confidence_score = int(response.strip())  # Corrected line
        return confidence_score >= 5  # Lowered threshold
    except ValueError:
        print("Invalid confidence score. Assuming non-deterministic question.")
        return False


def respond_to_question(agent, question):
    if not isinstance(question, str):  # Ensure question is a string
        question = str(question)
    messages = [HumanMessage(content=question)]
    response = agent.invoke(messages)
    response = response.content if hasattr(response, 'content') else response
    return str(response)  # Ensure the response is a string


def multi_dimensional_evaluation(judge, question, answer):
    dimensions = [
        "Accuracy: Was the answer factually correct? (0-10)",
        "Reasoning: Was the reasoning clear, logical, and coherent? (0-10)",
        "Efficiency: Was the answer concise and to the point? (0-10)",
        "Adaptability: Did the model handle unfamiliar concepts effectively? (0-10)",
        "Insightfulness: Did the answer provide additional valuable insights beyond the expected response? (0-10)"
    ]
    messages = [
        SystemMessage(
            content=f"Evaluate the following dimensions for the answer '{answer}' to the question '{question}':\n" + "\n".join(dimensions) + "\nReply with scores in the format: accuracy=8, reasoning=7, efficiency=9, adaptability=6, insightfulness=5."
        )
    ]
    response = judge.invoke(messages)
    response = response.content if hasattr(response, 'content') else response
    try:
        scores = {dim.split(':')[0].lower(): int(score.strip()) for dim, score in [item.split('=') for item in response.split(',')]}
        return scores
    except Exception:
        return {"accuracy": 0, "reasoning": 0, "efficiency": 0, "adaptability": 0, "insightfulness": 0}


# Role rotation function
def rotate_roles(round_num, start_index):
    asker1 = ai_models[(start_index + round_num) % 3]
    asker2 = ai_models[(start_index + round_num + 1) % 3]
    judge = ai_models[(start_index + round_num + 2) % 3]
    return asker1, asker2, judge

# Simulate one round
def play_round(round_num, start_index):
    asker1, asker2, judge = rotate_roles(round_num, start_index)

    # Each asker generates a question
    for asker, responder in [(asker1, asker2), (asker2, asker1)]:
        question = generate_question(asker)

        # Pre-validate determinism before answering
        attempts = 0
        while not validate_question_determinism(judge, question) and attempts < 3:
            print(f"Round {round_num + 1}: Question from {asker.name} was non-deterministic. Regenerating question...")
            question = generate_question(asker)
            attempts += 1

        if attempts == 3:
            print(f"Round {round_num + 1}: Failed to generate a deterministic question after 3 attempts. No points awarded.")
            scores[asker.name]["accuracy"] -= 0.5  # Apply penalty
            continue

        # Responder tries to answer
        answer = respond_to_question(responder, question)

        # Multi-dimensional evaluation
        eval_scores = multi_dimensional_evaluation(judge, question, answer)

        # Update scores
        for dimension, score in eval_scores.items():
            scores[responder.name][dimension] += score

        # Print result
        print(f"Round {round_num + 1}:")
        print("-" * 50)
        print(f"Question (from {asker.name} to {responder.name}): {question}")
        print(f"Answer (by {responder.name}): {answer}")
        print(f"Evaluation Scores: {eval_scores}\n")

# Run the game
def run_game(rounds=3):
    print(instructions)  # Display instructions before starting the game
    start_index = random.randint(0, 2)  # Randomize the first player
    for round_num in range(rounds):
        play_round(round_num, start_index)

    # Display final scores
    print("\nFinal Scores:")
    for model, model_scores in scores.items():
        total_score = sum(model_scores.values())
        print(f"{model}: Total = {total_score}, Breakdown = {model_scores}")

if __name__ == "__main__":
    run_game()
