from azure.servicebus import ServiceBusClient, ServiceBusMessage
from openai import OpenAI
import json
import time
import tiktoken  # Install using `pip install tiktoken`

# Azure Service Bus Configuration
CONNECTION_STRING = "Endpoint=sb://192.168.29.174;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"
QUEUE_NAME = "ngi_exp_request_queue"
NEW_QUEUE_NAME = "ngi_exp_response_queue"

# Disable TLS (Workaround for issue in Azure SDK)
from azure.servicebus._pyamqp import AMQPClient
org_init = AMQPClient.__init__
def new_init(self, hostname, **kwargs):
    kwargs["use_tls"] = False  # Disable TLS
    org_init(self, hostname, **kwargs)
AMQPClient.__init__ = new_init

# Initialize Service Bus Client
servicebus_client = ServiceBusClient.from_connection_string(CONNECTION_STRING)

# Dictionary to store data of 5 people
merged_data = {}

# Receive Messages & Merge Data for 5 Different personId's
with servicebus_client:
    receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, max_wait_time=5)

    with receiver:
        for message in receiver.receive_messages(max_message_count=20):  # Fetch messages
            msg_body = json.loads(str(message))
            person_id = msg_body.get("personId")

            if not person_id:
                print("⚠️ Message without personId, skipping.")
                continue

            # Initialize dictionary for each personId
            if person_id not in merged_data:
                merged_data[person_id] = {}  # Store each person's data as a dictionary

            # Merge data
            for key, value in msg_body.items():
                if key != "personId":  # Avoid duplicating personId
                    merged_data[person_id][key] = value

            print(f"📩 Received message for {person_id}: {msg_body}")
            receiver.complete_message(message)  # Mark message as processed

            # Stop after collecting data of 5 people
            if len(merged_data) == 5:
                print("✅ Collected data for 5 different people, stopping processing.")
                break

# Print the final merged data
print("\n🔹 Merged Data:")
print(json.dumps(merged_data, indent=4))

# Initialize OpenAI Client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"  # Replace with your actual key
)

# Construct prompt with all 5 people's data
prompt = f"Generate a different joke for each of these 5 people based on their details:\n{json.dumps(merged_data, indent=2)}"

# Count tokens
tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
num_tokens = len(tokenizer.encode(prompt))
print(f"🔢 Token Count: {num_tokens}")

# Measure API request execution time
start_time = time.time()
completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}]
)
end_time = time.time()
api_execution_time = end_time - start_time

# Extract AI Response
ai_response = completion.choices[0].message.content
print(f"\n🤖 AI Response:\n{ai_response}")
print(f"⏱ API Execution Time: {api_execution_time:.2f} seconds")

# Parse the AI response into individual jokes
jokes = ai_response.strip().split("\n\n")  # Split responses assuming newlines separate them

# Send AI Response to the new queue (split for each person)
with servicebus_client:
    response_sender = servicebus_client.get_queue_sender(NEW_QUEUE_NAME)
    with response_sender:
        for i, person_id in enumerate(merged_data.keys()):
            joke_text = jokes[i] if i < len(jokes) else "No joke available"
            ai_response_message = ServiceBusMessage(json.dumps({"personId": person_id, "response": joke_text}))
            response_sender.send_messages(ai_response_message)
            print(f"✅ AI Response for {person_id} sent to the queue '{NEW_QUEUE_NAME}'!")
