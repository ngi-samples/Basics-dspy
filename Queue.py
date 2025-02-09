from azure.servicebus import ServiceBusClient, ServiceBusMessage

# Connection string for Azure Service Bus Emulator
# CONNECTION_STRING = "Endpoint=sb://192.168.29.174;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"
CONNECTION_STRING = "Endpoint=sb://192.168.55.101;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"
QUEUE_NAME = "queue.1"

from azure.servicebus._pyamqp import AMQPClient
# Disable TLS. Workaround for https://github.com/Azure/azure-sdk-for-python/issues/34273
org_init = AMQPClient.__init__
def new_init(self, hostname, **kwargs):
    kwargs["use_tls"] = False
    org_init(self, hostname, **kwargs)
AMQPClient.__init__ = new_init

# # Initialize the Service Bus Client
servicebus_client = ServiceBusClient.from_connection_string(CONNECTION_STRING)



# Send a message to the queue
with servicebus_client:
    sender = servicebus_client.get_queue_sender(QUEUE_NAME)
    with sender:
        message = ServiceBusMessage("Hello, Service Bus Emulator!")
        sender.send_messages(message)
        print("✅ Message sent to the queue!")

# Receive the message to confirm it was sent
with servicebus_client:
    receiver = servicebus_client.get_queue_receiver(QUEUE_NAME, max_wait_time=5)
    with receiver:
        received_msgs = receiver.receive_messages()
        for msg in received_msgs:
            # Convert generator to string
            message_body = b"".join(msg.body).decode()  
            print(f"📩 Received message: {message_body}")


