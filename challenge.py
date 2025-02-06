import logging
import re
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Unified Instructions
instructions = open('prompts/instructions.md', 'r').read()

# Helper function to extract content safely
def extract_content(response):
    if isinstance(response, AIMessage):
        return response.content
    return str(response)

def extract_score(response_content):
    score = 0
    try:
        score = int(response_content.strip())
    except ValueError:
        match = re.search(r'(\d+)', response_content)
        if match:
            score = int(match.group(1))
        else:
            logging.error(f"Failed to extract score from response: {response_content}")
            score = 0
    finally:
        return max(0, min(10, score))

# Initialize scores and question history
scores = {}
dimension_scores = {}
question_history = []

# Mock functions for agent behavior
def generate_question(agent):
    challenge = open("prompts/challenge.md", "r").read()
    response = agent.invoke(challenge)
    question = extract_content(response)

    if question in question_history:
        return generate_question(agent)

    question_history.append(question)
    return question

def validate_question_determinism(judge, question):
    checklist = open('prompts/checklist.md', 'r').read()

    messages = [
        SystemMessage(content=instructions),
        SystemMessage(content='Act as a Judge'),
        HumanMessage(content=f"{checklist}\nQuestion: '{question}'\nRespond with a number from 0 to 10 only.")
    ]
    response = judge.invoke(messages)
    return extract_score(extract_content(response)) >= 7

def respond_to_question(agent, question):
    messages = [
        SystemMessage(content=instructions),
        SystemMessage(content='Act as a Responder'),
        HumanMessage(content=question)
    ]
    response = agent.invoke(messages)
    answer = extract_content(response)

    explanation_prompt = f"Please explain the reasoning behind your answer: '{answer}'."
    explanation_response = agent.invoke(explanation_prompt)
    explanation = extract_content(explanation_response)

    return answer, explanation

def evaluate_answer(evaluator, question, answer, explanation):
    criteria = {
        "Accuracy": "Is the answer factually accurate and supported by reliable information?",
        "Reasoning": "Does the answer reflect deep understanding, logical reasoning, and comprehensive analysis?",
        "Communication": "Is the answer clear, well-structured, concise, and easy to understand?"
    }
    scores = {}

    for crit, description in criteria.items():
        messages = [
            SystemMessage(content=instructions),
            SystemMessage(content='Act as a Judge'),
            HumanMessage(
                content=f"Evaluate the answer based on {crit}: {description}\nQuestion: '{question}'\nAnswer: '{answer}'\nExplanation: '{explanation}'\nProvide a score from 0 to 10 only."
            )
        ]
        response = evaluator.invoke(messages)
        scores[crit] = extract_score(extract_content(response))

    return scores

def evaluate_question(evaluator, question):
    question_criteria = {
        "Strategy": "Does the question strategically challenge the Responder's potential weaknesses and test critical thinking?",
        "Creativity": "Is the question original, engaging, thought-provoking, and designed to stimulate unique responses?"
    }
    scores = {}

    for crit, description in question_criteria.items():
        messages = [
            SystemMessage(content=instructions),
            SystemMessage(content='Act as a Judge'),
            HumanMessage(
                content=f"Evaluate the question based on {crit}: {description}\nQuestion: '{question}'\nProvide a score from 0 to 10 only."
            )
        ]
        response = evaluator.invoke(messages)
        scores[crit] = extract_score(extract_content(response))

    return scores

def play_round(round_num, ai_models):
    matches = [
        (ai_models[0], ai_models[1], ai_models[2]),
        (ai_models[1], ai_models[2], ai_models[0]),
        (ai_models[2], ai_models[0], ai_models[1])
    ]

    yield {'role': 'AI', 'content': f'**Round {round_num + 1}**'}

    for asker, responder, judge in matches:
        yield {'role': 'AI', 'content': f"**{asker.name}** will now pose a question to **{responder.name}**."}

        question = generate_question(asker)
        yield {'role': asker.name, 'content': question}

        attempts = 0
        while not validate_question_determinism(judge, question) and attempts < 3:
            yield {'role': judge.name, 'content': f"Non-deterministic question detected. Please regenerate..."}
            question = generate_question(asker)
            yield {'role': asker.name, 'content': question}
            attempts += 1

        if attempts == 3:
            if asker.name not in dimension_scores:
                dimension_scores[asker.name] = {"Accuracy": 0, "Reasoning": 0, "Communication": 0, "Strategy": 0, "Creativity": 0, "Count": 0}

            dimension_scores[asker.name]["Strategy"] += 0
            dimension_scores[asker.name]["Creativity"] += 0
            dimension_scores[asker.name]["Count"] += 1
            continue

        answer, explanation = respond_to_question(responder, question)
        yield {'role': responder.name, 'content': answer}
        yield {'role': responder.name, 'content': explanation}

        asker_answer_eval = evaluate_answer(asker, question, answer, explanation)
        yield {'role': asker.name, 'content': f"Evaluating **{responder.name}'s** answer: {asker_answer_eval}"}

        judge_answer_eval = evaluate_answer(judge, question, answer, explanation)
        yield {'role': judge.name, 'content': f"Evaluating **{responder.name}'s** answer: {judge_answer_eval}"}

        final_scores = {key: round((asker_answer_eval[key] + judge_answer_eval[key]) / 2, 2) for key in asker_answer_eval}
        yield {'role': 'AI', 'content': f"**{responder.name}** answer scores: {final_scores}"}

        for dim in final_scores:
            dimension_scores[responder.name][dim] += final_scores[dim]
        dimension_scores[responder.name]["Count"] += 1

        responder_question_eval = evaluate_question(responder, question)
        yield {'role': responder.name, 'content': f"Evaluating **{asker.name}'s** question: {responder_question_eval}"}

        judge_question_eval = evaluate_question(judge, question)
        yield {'role': judge.name, 'content': f"Evaluating **{asker.name}'s** question: {judge_question_eval}"}

        final_asker_scores = {key: round((responder_question_eval[key] + judge_question_eval[key]) / 2, 2)
                              for key in responder_question_eval}
        yield {'role': 'AI', 'content': f"**{asker.name}** question scores: {final_asker_scores}"}

        for dim in final_asker_scores:
            dimension_scores[asker.name][dim] += final_asker_scores[dim]
        dimension_scores[asker.name]["Count"] += 1

def run_game(rounds, competitors_arr):
    from langchain_openai import ChatOpenAI
    from langchain_google_vertexai import VertexAI
    from langchain_deepseek import ChatDeepSeek
    from langchain_anthropic import ChatAnthropic

    try:
        agents = []
        for competitor in competitors_arr:
            if competitor['type'] == 'openai':
                agent = ChatOpenAI(model_name=competitor['model'], temperature=1)
            elif competitor['type'] == 'vertexai':
                location = competitor.get('location', "us-central1")
                agent = VertexAI(model_name=competitor['model'], temperature=1, location=location)
            elif competitor['type'] == 'deepseek':
                agent = ChatDeepSeek(model_name=competitor["model"], temperature=1)
            elif competitor['type'] == 'anthropic':
                agent = ChatAnthropic(model_name=competitor["model"], temperature=1)
            agent.name = competitor['name']
            agents.append(agent)

        global scores, dimension_scores
        scores = {model.name: 0 for model in agents}
        dimension_scores = {
            model.name: {"Accuracy": 0, "Reasoning": 0, "Communication": 0, "Strategy": 0, "Creativity": 0, "Count": 0}
            for model in agents
        }

        yield {'role': 'AI', 'content': instructions}

        competitors_md = """
**Please welcome our competitors:**

| AI Model    | Model in Use         |
|-------------|----------------------|
"""

        # Adding Competitors
        for competitor in competitors_arr:
            competitors_md += f"| {competitor['name']} | {competitor['model']} |\n"

        yield {'role': 'AI', 'content': competitors_md}

        for round_num in range(rounds):
            yield from play_round(round_num, agents)

        final_summary_md = """
**End of Game Scores**

| AI Model | Total Score | Accuracy | Reasoning | Communication | Strategy | Creativity |
|:---------|------------:|---------:|----------:|--------------:|---------:|-----------:|
"""
        for model in scores.keys():
            count = dimension_scores[model]['Count'] or 1
            avg_accuracy = round((dimension_scores[model]['Accuracy'] / count) * 2, 2)
            avg_reasoning = round((dimension_scores[model]['Reasoning'] / count) * 2, 2)
            avg_communication = round((dimension_scores[model]['Communication'] / count) * 2, 2)
            avg_strategy = round((dimension_scores[model]['Strategy'] / count) * 2, 2)
            avg_creativity = round((dimension_scores[model]['Creativity'] / count) * 2, 2)

            total_score = round((avg_accuracy + avg_reasoning + avg_communication + avg_strategy + avg_creativity) / 5, 2)

            final_summary_md += (f"| {model} | {total_score} "
                                 f"| {avg_accuracy} "
                                 f"| {avg_reasoning} "
                                 f"| {avg_communication} "
                                 f"| {avg_strategy} "
                                 f"| {avg_creativity} |\n")

        yield {'role': 'AI', 'content': final_summary_md}
    except Exception as ex:
        yield {'role': 'AI', 'content': f"Error: {ex}"}