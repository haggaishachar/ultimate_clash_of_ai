# Ultimate Clash of AI

## Overview

**Ultimate Clash of AI** is a novel AI evaluation platform designed as an interactive game where leading AI models compete against each other. 
This project introduces an innovative **peer supervision approach** to measure the quality of AI models through dynamic, role-based interactions. By having AI models act as **Askers**, **Responders**, and **Judges**, we create an environment where AI models evaluate each other's performance across multiple dimensions, providing a robust and unbiased assessment framework.

## Key Features

- **Role-Based Gameplay:** Each AI model takes on rotating roles:

  - **Asker:** Generates deterministic, factual, and verifiable questions and evaluates the Responder's performance.
  - **Responder:** Provides accurate answers with clear reasoning and communication while also evaluating the Asker's question.
  - **Judge:** Evaluates both the quality of the question and the answer.

- **Multi-Dimensional Evaluation:** Models are assessed based on:

  - **For Responders:** Accuracy, Reasoning, and Communication.
  - **For Askers:** Strategy and Creativity.

- **Peer Supervision:** Models critique each other's performance, ensuring objective, self-regulating evaluation without human bias.

## How It Works

**In each round:**

- **Each model becomes the Asker twice**, posing questions to the other models and evaluating the Responder's performance.
- **Each model responds twice**, answering questions and evaluating the Asker's question.
- **Each model judges once**, evaluating both the Asker and the Responder.

The scoring system aggregates evaluations to determine the best-performing AI model based on its questioning, answering, and judging skills.

### Scoring System

- **Scores range from 0 to 10** for each evaluation criterion:
  - **0** indicates poor performance or non-compliance with the evaluation criteria.
  - **10** indicates exceptional performance, demonstrating the highest standard in accuracy, reasoning, communication, strategy, or creativity.

Scores are **averaged between the Judge's evaluation and the evaluation from the other AI model** involved in the round (either the Asker or the Responder). This approach ensures balanced, peer-reviewed scoring.

## Game On

You can run the app in two modes:

1. **🎲 Simulation Mode:**

   - Loads historical threads stored in the `challenges` directory.
   - Allows you to review past challenges, questions, answers, and evaluations.

2. **⚡ Live Mode:**

   - Runs a live challenge where AI models actively generate questions, respond, and evaluate each other in real-time.

Select the desired mode from the sidebar when running the app.

## Run Locally

### Prerequisites

- Python 3.10+
- `pip` for package management

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/haggaishachar/ultimate-clash-of-ai.git
   cd ultimate-clash-of-ai
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**

   - Add your API keys for AI model integrations:
     - `OPENAI_API_KEY` (for ChatGPT)
     - `ANTHROPIC_API_KEY` (for Claude)
   - Ensure you are authenticated with Google Cloud Platform (GCP) for Vertex AI (Gemini).
   - Alternatively, you can store these keys in a `.env` file in the project directory:

     ```bash
     OPENAI_API_KEY=your_openai_api_key
     ANTHROPIC_API_KEY=your_anthropic_api_key
     ```

4. **Run the application:**

   ```bash
   streamlit run app.py
   ```

## Contribution

Contributions are welcome!\
Feel free to fork the repository, submit issues, and create pull requests to improve the project.

## License

This project is licensed under the **MIT License**. 

# Let the Ultimate Clash of AI begin!
