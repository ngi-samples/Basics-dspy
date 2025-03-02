Hello First Install docker desktop and requirements


1. How long does a API call to LLM take?

`API Execution Time: 2.86 seconds` is the general time taken by api call to llm take


2. ⁠Which is best and why? Sending all users data in a single request to LLM and get all the respective user’s jokes in a single LLM response? or one request per user or one request for a batch of users?

`For up to ~5 users → A single request is best (unless token limits are exceeded).`
`For 10+ users → Batch processing (2-5 users per request) is the optimal balance.`
`If real-time response is required per user → Per-user requests are better but costly.`


3. I see you have used tiktoken which is good. And, does the AI response include headers or body that will tell us how many  requests are pending and how many tokens left, before we hit the rate limits?

`In the free tier of the llm 's api the headers are not included even when we fetch using the header.py we get none as the result for every request.`