from azure.servicebus import ServiceBusClient, ServiceBusMessage
from openai import OpenAI
import json

# Azure Service Bus Configuration
CONNECTION_STRING = "Endpoint=sb://192.168.0.6;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"
QUEUE_NAME = "ngi_exp_request_queue"
NEW_QUEUE_NAME = "ngi_exp_response_queue"  # New queue for AI responses

# Disable TLS (Workaround for Azure SDK issue)
from azure.servicebus._pyamqp import AMQPClient

org_init = AMQPClient.__init__
def new_init(self, hostname, **kwargs):
    kwargs["use_tls"] = False  # Disable TLS
    org_init(self, hostname, **kwargs)
AMQPClient.__init__ = new_init

# Initialize Service Bus Client
servicebus_client = ServiceBusClient.from_connection_string(CONNECTION_STRING)

# Dictionary to store merged data
merged_data = {}
first_person_id = None

# Receive Messages & Merge Data
with servicebus_client:
    receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, max_wait_time=5)
    
    with receiver:
        for message in receiver.receive_messages(max_message_count=10):  # Adjust count as needed
            msg_body = json.loads(str(message))
            current_person_id = msg_body.get("personId")

            # If first message, initialize personId tracking
            if first_person_id is None:
                first_person_id = current_person_id
                merged_data["personId"] = first_person_id

            # Stop if a different personId is encountered
            if current_person_id != first_person_id:
                print(f"🚫 Different personId ({current_person_id}) found, stopping processing.")
                break

            # Merge the data into `merged_data`
            for key, value in msg_body.items():
                if key == "personId":
                    continue  # Already set
                if key in merged_data and isinstance(merged_data[key], dict) and isinstance(value, dict):
                    merged_data[key].update(value)  # Merge nested dictionaries
                else:
                    merged_data[key] = value  # Update other fields

            print(f"📩 Received message: {msg_body}")
            receiver.complete_message(message)  # Mark message as processed

# Print the final merged data
print("\n🔹 Merged Data:")
print(json.dumps(merged_data, indent=4))

# Initialize OpenAI Client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"  # Replace with your actual key
)

# Send `merged_data` to OpenAI API
completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": f"Tell me a joke about this person: {json.dumps(merged_data)}"}]
)

# Extract AI Response
ai_response = completion.choices[0].message.content
print("\n🤖 AI Response:", ai_response)

# Send AI Response to the new queue
with servicebus_client:
    response_sender = servicebus_client.get_queue_sender(NEW_QUEUE_NAME)
    with response_sender:
        ai_response_message = ServiceBusMessage(ai_response)
        response_sender.send_messages(ai_response_message)
        print(f"✅ AI Response sent to the new queue '{NEW_QUEUE_NAME}'!")
