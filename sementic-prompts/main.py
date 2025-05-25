# import os
# from dotenv import load_dotenv
# import dspy
# from dspy.LM import OpenAI 

# # Load your .env file
# load_dotenv()

# # Configure the LLM (e.g., GPT-3.5)
# dspy.settings.configure(lm=OpenAI(model="gpt-3.5-turbo"))

# # Define the signature
# class AnswerQuestion(dspy.Signature):
#     question = dspy.InputField()
#     answer = dspy.OutputField(desc="A factual and concise answer")

# # Create the reasoning module
# cot = dspy.ChainOfThought(signature=AnswerQuestion)

# # Run it
# response = cot(question="Why do leaves change color in the fall?")
# print("Answer:", response.answer)
from dspy.clients.openai import openai

# Example usage:
configure(lm=OpenAI(model="gpt-3.5-turbo"))
print(lm)
