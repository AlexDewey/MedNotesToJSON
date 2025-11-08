from ollama import chat
from ollama import ChatResponse

def get_response(model, medData, format=None):

    if format is None:
        response: ChatResponse = chat(model=model, messages=[
            {
                'role': 'user',
                'content': f'{medData}',
            },
            ])
        return response.message.content
    else:
        response: ChatResponse = chat(model=model, messages=[
        {
            'role': 'user',
            'content': f'{medData}',
        },
        ],
        format=format.model_json_schema())

        return format.model_validate_json(response.message.content)