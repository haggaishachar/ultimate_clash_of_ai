from langchain_anthropic import ChatAnthropic
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
import dotenv

dotenv.load_dotenv()

# model = 'claude-3-haiku-20240307'
# model = 'claude-3-opus-20240229'
model = 'gemini-2.0-pro-exp-02-05'
ai = ChatVertexAI(model_name=model, temperature=1)

question = """" 
Given a standard 8x8 chessboard, a hypothetical piece called the "Chancellor" combines the moves of a Rook and a Knight (can move any number of squares horizontally or vertically OR move in an "L" shape: two squares in one direction and then one square perpendicularly).

If a Chancellor starts on the square A1 (bottom left), what is the minimum number of moves required for it to reach the square H8 (top right), assuming no other pieces are on the board?
"""

res = ai.invoke([HumanMessage(content=question)])

print(res)