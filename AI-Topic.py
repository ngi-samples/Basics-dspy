from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.servicebus._pyamqp import AMQPClient
from openai import OpenAI

# Azure Service Bus Emulator Connection String
CONNECTION_STRING = "Endpoint=sb://192.168.29.174;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"

# Topics and Subscriptions
REQUEST_TOPIC_NAME = "ngi_exp_request_topic"
RESPONSE_TOPIC_NAME = "ngi_exp_response_topic"
REQUEST_SUBSCRIPTION_NAME = "request_subscription_1"

# Disable TLS (Workaround for issue in Azure SDK)
org_init = AMQPClient.__init__
def new_init(self, hostname, **kwargs):
    kwargs["use_tls"] = False  # Disable TLS
    org_init(self, hostname, **kwargs)
AMQPClient.__init__ = new_init

# Initialize Service Bus Client
servicebus_client = ServiceBusClient.from_connection_string(CONNECTION_STRING)

# Send a test message to ngi_exp_request_topic
with servicebus_client:
    sender = servicebus_client.get_topic_sender(REQUEST_TOPIC_NAME)
    with sender:
        test_message = ServiceBusMessage("Hello, AI! Process this message.")
        sender.send_messages(test_message)
        print(f"📤 Sent message to '{REQUEST_TOPIC_NAME}'")

with servicebus_client:
    receiver = servicebus_client.get_subscription_receiver(
        topic_name=REQUEST_TOPIC_NAME,
        subscription_name=REQUEST_SUBSCRIPTION_NAME,
        max_wait_time=5
    )
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

            # Send request to OpenAI API
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message_body}]
            )

            # Get AI response
            ai_response = completion.choices[0].message.content
            print("🤖 AI Response:", ai_response)

            # Mark message as processed
            receiver.complete_message(msg)

            # Send AI response to response topic
            with servicebus_client:
                sender = servicebus_client.get_topic_sender(RESPONSE_TOPIC_NAME)
                with sender:
                    response_message = ServiceBusMessage(ai_response)
                    sender.send_messages(response_message)
                    print(f"✅ AI Response sent to '{RESPONSE_TOPIC_NAME}'")
