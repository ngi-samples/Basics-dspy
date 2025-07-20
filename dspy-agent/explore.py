import dspy

# Check if Gemini is available as a provider
print(hasattr(dspy.clients, "gemini"))
print(hasattr(dspy.clients, "google"))