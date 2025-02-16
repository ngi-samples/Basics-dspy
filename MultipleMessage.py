from azure.servicebus import ServiceBusClient, ServiceBusMessage
import json

# Azure Service Bus Connection String (Local Emulator or Cloud)
CONNECTION_STRING = "Endpoint=sb://192.168.0.6;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"
QUEUE_NAME = "ngi_exp_request_queue"

# Disable TLS (Workaround for issue in Azure SDK)
from azure.servicebus._pyamqp import AMQPClient
org_init = AMQPClient.__init__
def new_init(self, hostname, **kwargs):
    kwargs["use_tls"] = False  # Disable TLS
    org_init(self, hostname, **kwargs)
AMQPClient.__init__ = new_init

# User A's Data Split into Multiple Messages
user_a_messages = [
    {
        "personId": "12345",  # Unique identifier for User A
        "firstName": "John",
        "lastName": "Doe",
        "email": "johndoe@example.com"
    },  # Message 1 - Basic Details
    {
        "personId": "12345",
        "phone": "+1-555-9876",
        "address": {
            "street": "789 Pine Street",
            "city": "Boston",
            "state": "MA",
            "zipCode": "02108"
        }
    },  # Message 2 - Contact Details Update
    {
        "personId": "12345",
        "employment": {
            "company": "TechCorp",
            "position": "Senior Software Engineer",
            "startDate": "2023-01-10"
        }
    },  # Message 3 - Employment Details
    {
        "personId": "12345",
        "email": "john.doe@techcorp.com"
    }  # Message 4 - Email Update
]

# User B's Data Split into Multiple Messages
user_b_messages = [
    {
        "personId": "67890",  # Unique identifier for User B
        "firstName": "Jane",
        "lastName": "Smith",
        "email": "janesmith@example.com"
    },  # Message 1 - Basic Details
    {
        "personId": "67890",
        "phone": "+1-555-1234",
        "address": {
            "street": "456 Elm Street",
            "city": "New York",
            "state": "NY",
            "zipCode": "10001"
        }
    },  # Message 2 - Contact Details Update
    {
        "personId": "67890",
        "employment": {
            "company": "DataCorp",
            "position": "Data Scientist",
            "startDate": "2022-05-15"
        }
    },  # Message 3 - Employment Details
    {
        "personId": "67890",
        "email": "jane.smith@datacorp.com"
    }  # Message 4 - Email Update
]

# Combine Messages for Both Users
all_messages = user_a_messages + user_b_messages

# Create Service Bus Client
servicebus_client = ServiceBusClient.from_connection_string(CONNECTION_STRING)

# Send Messages to Queue
with servicebus_client:
    sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
    with sender:
        for msg in all_messages:
            # Serialize the message to JSON and send it to the queue
            servicebus_msg = ServiceBusMessage(json.dumps(msg))
            sender.send_messages(servicebus_msg)
            print(f"Sent message: {msg}")

print("All messages for User A and User B sent successfully!")