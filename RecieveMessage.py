import aiohttp
import asyncio
import json
import time
import tiktoken
from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient

# Azure Service Bus Configuration
CONNECTION_STRING = "Endpoint=sb://192.168.0.3;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=SAS_KEY_VALUE;UseDevelopmentEmulator=true;"
QUEUE_NAME = "ngi_exp_request_queue"
NEW_QUEUE_NAME = "ngi_exp_response_queue"

# Dictionary to store data of 5 people
merged_data = {}

from azure.servicebus._pyamqp import AMQPClient
org_init = AMQPClient.__init__
def new_init(self, hostname, **kwargs):
    kwargs["use_tls"] = False
    org_init(self, hostname, **kwargs)
AMQPClient.__init__ = new_init

# ✅ Async function to receive messages
async def receive_messages():
    async with ServiceBusClient.from_connection_string(CONNECTION_STRING) as servicebus_client:
        async with servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, max_wait_time=5) as receiver:
            messages = await receiver.receive_messages(max_message_count=20)
            
            for message in messages:
                msg_body = json.loads(str(message))
                person_id = msg_body.get("personId")

                if not person_id:
                    print("⚠️ Message without personId, skipping.")
                    await receiver.complete_message(message)
                    continue

                if person_id not in merged_data:
                    merged_data[person_id] = {}
                
                for key, value in msg_body.items():
                    if key != "personId":
                        merged_data[person_id][key] = value

                print(f"📩 Received message for {person_id}: {msg_body}")
                await receiver.complete_message(message)

                # Stop after collecting data for 5 people
                if len(merged_data) == 5:
                    print("✅ Collected data for 5 different people, stopping processing.")
                    break

# ✅ Async function to make API calls using aiohttp
async def fetch_openai_response(session, prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer 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",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }
    async with session.post(url, headers=headers, json=data) as response:
        result = await response.json()
        return result["choices"][0]["message"]["content"]

# ✅ Function to create prompts
def create_prompt():
    return f"Generate a different joke for each of these 5 people based on their details:\n{json.dumps(merged_data, indent=2)}"

# ✅ Async function to call OpenAI API concurrently
async def get_ai_responses():
    prompt = create_prompt()
    tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
    num_tokens = len(tokenizer.encode(prompt))
    print(f"🔢 Token Count: {num_tokens}")

    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        tasks = [fetch_openai_response(session, prompt) for _ in merged_data]
        responses = await asyncio.gather(*tasks)
        end_time = time.time()

        print(f"⏱ API Execution Time: {end_time - start_time:.2f} seconds")
        return responses

# ✅ Async function to send responses to Azure Service Bus
async def send_responses(responses):
    async with ServiceBusClient.from_connection_string(CONNECTION_STRING) as servicebus_client:
        async with servicebus_client.get_queue_sender(NEW_QUEUE_NAME) as response_sender:
            for i, (person_id, response) in enumerate(zip(merged_data.keys(), responses)):
                ai_response_message = ServiceBusMessage(json.dumps({"personId": person_id, "response": response}))
                await response_sender.send_messages(ai_response_message)
                print(f"✅ AI Response for {person_id} sent to the queue '{NEW_QUEUE_NAME}'!")

# ✅ Main function to orchestrate the flow
async def main():
    await receive_messages()
    if len(merged_data) == 0:
        print("❗ No messages received.")
        return
    
    responses = await get_ai_responses()
    await send_responses(responses)

# Run the async event loop
asyncio.run(main())
