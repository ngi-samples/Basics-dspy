from azure.servicebus import ServiceBusClient, ServiceBusMessage
import json
import time

# Azure Service Bus Connection String (Local Emulator or Cloud)
CONNECTION_STRING = "Endpoint=sb://192.168.29.174;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"
QUEUE_NAME = "ngi_exp_request_queue"

# Disable TLS (Workaround for issue in Azure SDK)
from azure.servicebus._pyamqp import AMQPClient
org_init = AMQPClient.__init__
def new_init(self, hostname, **kwargs):
    kwargs["use_tls"] = False  # Disable TLS
    org_init(self, hostname, **kwargs)
AMQPClient.__init__ = new_init

# Generate data for 10 users
users_data = []
for i in range(1, 11):
    person_id = str(10000 + i)  # Unique identifier
    users_data.extend([
        {  # Message 1 - Basic Details
            "personId": person_id,
            "firstName": f"User{i}",
            "lastName": "Test",
            "email": f"user{i}@example.com"
        },
        {  # Message 2 - Contact Details Update
            "personId": person_id,
            "phone": f"+1-555-100{i}",
            "address": {
                "street": f"{i} Main Street",
                "city": "CityX",
                "state": "StateY",
                "zipCode": f"1234{i}"
            }
        },
        {  # Message 3 - Employment Details
            "personId": person_id,
            "employment": {
                "company": f"Company{i}",
                "position": "Developer",
                "startDate": f"202{i}-01-01"
            }
        },
        {  # Message 4 - Email Update
            "personId": person_id,
            "email": f"user{i}@company{i}.com"
        }
    ])

# Measure start time
start_time = time.time()

# Create Service Bus Client
servicebus_client = ServiceBusClient.from_connection_string(CONNECTION_STRING)

# Send Messages to Queue
with servicebus_client:
    sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
    with sender:
        for msg in users_data:
            servicebus_msg = ServiceBusMessage(json.dumps(msg))
            sender.send_messages(servicebus_msg)
            print(f"Sent message: {msg}")

# Measure end time and calculate execution time
end_time = time.time()
execution_time = end_time - start_time
print(f"All messages for 10 users sent successfully! Execution Time: {execution_time:.2f} seconds")
