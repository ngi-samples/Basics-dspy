from azure.servicebus import ServiceBusClient, ServiceBusMessage
from openai import OpenAI
from azure.servicebus.management import ServiceBusAdministrationClient

# Connection string for Azure Service Bus Emulator
CONNECTION_STRING = "Endpoint=sb://192.168.29.174;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"
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
            ai_response = completion.choices[0].message.content
            print("🤖 AI Response:", ai_response)
            
            # Mark the message as processed
            receiver.complete_message(msg)
            
            # Send the AI response to the new queue
            with servicebus_client:
                new_queue_sender = servicebus_client.get_queue_sender(NEW_QUEUE_NAME)
                with new_queue_sender:
                    ai_response_message = ServiceBusMessage(ai_response)
                    new_queue_sender.send_messages(ai_response_message)
                    print(f"✅ AI Response sent to the new queue '{QUEUE_NAME}'!")