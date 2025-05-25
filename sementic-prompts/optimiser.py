import os
from dotenv import load_dotenv
import dspy
from dspy import Signature, InputField, OutputField, Example
from dspy.teleprompt import BootstrapFewShotWithRandomSearch

# Load your OpenAI key
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Set up DSPy to use OpenAI
from dspy.clients import openai as openai_client
lm = openai_client.OpenAI(model="gpt-3.5-turbo")
dspy.settings.configure(lm=lm)

# Define a Signature (like a prompt contract)
class ParaphraseTask(Signature):
    """Reword the input sentence while keeping its original meaning."""
    sentence = InputField()
    paraphrase = OutputField()

# Define a DSPy Module
class Paraphraser(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(ParaphraseTask)

    def forward(self, sentence):
        return self.predict(sentence=sentence)

# Training (optimization) data
train_set = [
    Example(sentence="I love playing football.").with_outputs(paraphrase="Football is one of my favorite activities."),
    Example(sentence="She went to the market to buy vegetables.").with_outputs(paraphrase="She visited the market to purchase veggies."),
    Example(sentence="The weather is nice today.").with_outputs(paraphrase="It's a pleasant day weather-wise."),
]

# Evaluation set (can also be separate)
dev_set = [
    Example(sentence="He is reading a book.").with_outputs(paraphrase="He's engaged in reading a book."),
]

# Choose an optimizer
optimizer = BootstrapFewShotWithRandomSearch(metric="exact_match", max_bootstraps=3)

# Optimize the module
optimized_module = optimizer.compile(Paraphraser(), train_set=train_set, eval_set=dev_set)

# Test it!
prediction = optimized_module(sentence="They are watching a movie.")
print("Prediction:", prediction.paraphrase)
