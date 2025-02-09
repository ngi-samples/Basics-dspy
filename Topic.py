from azure.servicebus import ServiceBusClient, ServiceBusMessage

# Azure Service Bus Connection String
CONNECTION_STRING = "Endpoint=sb://172.18.32.1;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"

TOPIC_NAME = "topic.1"  # Replace with your topic name
SUBSCRIPTION_NAME = "subscription.3"  # Replace with your subscription name

from azure.servicebus._pyamqp import AMQPClient

# Disable TLS - Workaround for Azure SDK issue
org_init = AMQPClient.__init__
def new_init(self, hostname, **kwargs):
    kwargs["use_tls"] = False
    org_init(self, hostname, **kwargs)
AMQPClient.__init__ = new_init

# Initialize the Service Bus Client
servicebus_client = ServiceBusClient.from_connection_string(CONNECTION_STRING)

# Send a message to the topic
with servicebus_client:
    sender = servicebus_client.get_topic_sender(TOPIC_NAME)
    with sender:
        message = ServiceBusMessage("Hello, Service Bus Topic!")
        sender.send_messages(message)
        print("✅ Message sent to the topic!")

# Receive messages from the topic's subscription
with servicebus_client:
    receiver = servicebus_client.get_subscription_receiver(TOPIC_NAME, SUBSCRIPTION_NAME, max_wait_time=10)
    with receiver:
        received_msgs = receiver.receive_messages()
        for msg in received_msgs:
            message_body = b"".join(msg.body).decode()  # Convert to string
            print(f"📩 Received message from subscription: {message_body}")
            receiver.complete_message(msg)  # Mark as complete
