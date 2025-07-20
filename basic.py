import dspy
import os
from dotenv import load_dotenv  # Add this import

load_dotenv()  # Load environment variables from .env

gemini_api_key = os.getenv("GEMINI_API_KEY")  # Read from .env

gemini_model_name = "gemini/gemini-2.5-flash"

try:
    lm = dspy.LM(model=gemini_model_name, api_key=gemini_api_key)
    dspy.configure(lm=lm)
    print(f"DSPy configured with model: {gemini_model_name}")
except Exception as e:
    print(f"Error configuring DSPy: {e}")
    print("Please ensure your API key is correct and the model name is valid.")
    exit()

print("\n--- Testing Direct LM Calls ---")
try:
    response_1 = lm("Say this is a test!", temperature=0.7)
    print(f"LM Response (simple string prompt): {response_1}")

    response_2 = lm(messages=[{"role": "user", "content": "Say this is a test!"}])
    print(f"LM Response (messages prompt): {response_2}")

except Exception as e:
    print(f"\nAn error occurred during direct LM testing: {e}")
    print("This might be due to an invalid API key, an issue with the Gemini service, or rate limits.")

print("\n--- Executing ChainOfThought Example ---")

try:
    math_cot = dspy.ChainOfThought("question -> answer: float")

    question_text = "Two dice are tossed. What is the probability that the sum equals two?"
    print(f"Question: {question_text}")

    prediction = math_cot(question=question_text)

    full_answer_text = prediction.answer
    if isinstance(full_answer_text, str) and "Answer:" in full_answer_text:
        thought_process = full_answer_text.split("Answer:")[0].strip()
        final_answer = full_answer_text.split("Answer:")[1].strip()
        print(f"\nThought Process:\n{thought_process}")
        print(f"Final Answer: {final_answer}")
    else:
        print(f"\nFull Response: {full_answer_text}")

except Exception as e:
    print(f"\nAn error occurred during ChainOfThought execution: {e}")
    print("This might be due to an invalid API key, an issue with the Gemini service, or rate limits.")
    print("Also, ensure the model can handle the 'float' output constraint or adjust the signature if needed.")
