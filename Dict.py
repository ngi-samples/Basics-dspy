from azure.servicebus import ServiceBusClient, ServiceBusMessage
from openai import OpenAI
from azure.servicebus.management import ServiceBusAdministrationClient
import json
import time

# Connection string for Azure Service Bus Emulator
CONNECTION_STRING = "Endpoint=sb://192.168.0.11;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"
QUEUE_NAME = "ngi_exp_request_queue"
NEW_QUEUE_NAME = "ngi_exp_response_queue"  # Name of the new queue for AI responses

# Initialize the Service Bus Administration Client
admin_client = ServiceBusAdministrationClient.from_connection_string(CONNECTION_STRING)

# Disable TLS (Workaround for issue in azure-sdk)
from azure.servicebus._pyamqp import AMQPClient

org_init = AMQPClient.__init__
def new_init(self, hostname, **kwargs):
    kwargs["use_tls"] = False  # Disable TLS
    org_init(self, hostname, **kwargs)
AMQPClient.__init__ = new_init

# Initialize the Service Bus Client
servicebus_client = ServiceBusClient.from_connection_string(CONNECTION_STRING)

# Send multiple messages to the queue
messages_to_send = [
    {"name": "Uzair"},
    {"hobby": "coding"},
    {"fav_language": "Python"}
]

with servicebus_client:
    sender = servicebus_client.get_queue_sender(QUEUE_NAME)
    with sender:
        for data in messages_to_send:
            message = ServiceBusMessage(json.dumps(data))
            sender.send_messages(message)
        print("✅ Messages sent to the queue!")

# Receive multiple messages from the queue and ensure all required data is collected
collected_data = {}
expected_keys = {"name", "hobby", "fav_language"}

with servicebus_client:
    receiver = servicebus_client.get_queue_receiver(QUEUE_NAME, max_wait_time=10)
    with receiver:
        while expected_keys - collected_data.keys():  # Keep receiving until all keys are collected
            received_msgs = receiver.receive_messages()
            for msg in received_msgs:
                message_body = json.loads(b"".join(msg.body).decode())  # Convert generator to JSON
                collected_data.update(message_body)  # Merge received data
                receiver.complete_message(msg)  # Mark message as processed
                if expected_keys - collected_data.keys():
                    time.sleep(2)  # Small delay to wait for remaining messages

# Convert collected data to JSON
collected_data_json = json.dumps(collected_data)
print("📩 Collected Data from queue:", collected_data_json)

# Initialize OpenAI client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"  # Replace with your actual key
)

# Send the collected data to OpenAI API to generate a joke
completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": f"Hey, tell me a joke based on this data: {collected_data_json}"}]
)

# Print AI response
ai_response = completion.choices[0].message.content
print("🤖 AI Response:", ai_response)

# Send the AI response to the new queue
with servicebus_client:
    new_queue_sender = servicebus_client.get_queue_sender(NEW_QUEUE_NAME)
    with new_queue_sender:
        ai_response_message = ServiceBusMessage(ai_response)
        new_queue_sender.send_messages(ai_response_message)
        print(f"✅ AI Response sent to the new queue '{NEW_QUEUE_NAME}'!")
