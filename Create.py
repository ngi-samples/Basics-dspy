from azure.servicebus import ServiceBusClient, ServiceBusMessage
from openai import OpenAI

# Connection string for Azure Service Bus Emulator
CONNECTION_STRING = "Endpoint=sb://192.168.55.101;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"
QUEUE_NAME = "queue.1"

from azure.servicebus._pyamqp import AMQPClient
# Disable TLS (Workaround for issue in azure-sdk)
org_init = AMQPClient.__init__

def new_init(self, hostname, **kwargs):
    kwargs["use_tls"] = False  # Disable TLS
    org_init(self, hostname, **kwargs)

AMQPClient.__init__ = new_init

# Initialize the Service Bus Client
servicebus_client = ServiceBusClient.from_connection_string(CONNECTION_STRING)

# Send a message to the queue
with servicebus_client:
    sender = servicebus_client.get_queue_sender(QUEUE_NAME)
    with sender:
        message = ServiceBusMessage("Hello, Service Bus Emulator!")
        sender.send_messages(message)
        print("✅ Message sent to the queue!")

# Receive the message from the queue
with servicebus_client:
    receiver = servicebus_client.get_queue_receiver(QUEUE_NAME, max_wait_time=5)
    with receiver:
        received_msgs = receiver.receive_messages()
        for msg in received_msgs:
            message_body = b"".join(msg.body).decode()  # Convert generator to string
            print(f"📩 Received message: {message_body}")

            # Initialize OpenAI client
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key="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"  # Replace with your actual key
            )

            # Send the received message to OpenAI API once
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message_body}]
            )

            # Print AI response once
            print("🤖 AI Response:", completion.choices[0].message.content)

            # Mark the message as processed
            receiver.complete_message(msg)