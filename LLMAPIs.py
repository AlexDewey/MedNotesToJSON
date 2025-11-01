from ollama import chat
from ollama import ChatResponse

def get_response(model, medData):

    response: ChatResponse = chat(model=model, messages=[
    {
        'role': 'user',
        'content': f'{medData}',
    },
    ])

    return response.message.content