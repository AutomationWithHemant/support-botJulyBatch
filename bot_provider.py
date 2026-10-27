# bot_provider.py  -  lets PromptFoo call OUR RAG bot's ask() function
from rag_bot import ask

def call_api(prompt, options, context):
    # PromptFoo sends the rendered question as 'prompt'
    answer = ask(prompt)
    return {"output": answer}
