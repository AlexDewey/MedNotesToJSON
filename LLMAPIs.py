from ollama import chat
from ollama import ChatResponse

def get_response(model, system_prompt, user_prompt, format=None):

    if format is None:
        response: ChatResponse = chat(model=model, messages=[
            {
                'role': 'system',
                'content': f'{system_prompt}'
            },
            {
                'role': 'user',
                'content': f'{user_prompt}'
            },
            ])
        return response.message.content
    else:
        response: ChatResponse = chat(model=model, messages=[
        {
            'role': 'system',
            'content': f'{system_prompt}'
        },
        {
            'role': 'user',
            'content': f'{user_prompt}'
        },
        ],
        format=format.model_json_schema())

        return format.model_validate_json(response.message.content)