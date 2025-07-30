import os

import httpx
import openai
from dotenv import load_dotenv
from pydantic import BaseModel

from automcp.errors import ModelNotFoundError, NoResponseFromModelError

class LLMClient:
    def __init__(self):
        load_dotenv()
        self.model_name = os.getenv("MODEL_NAME", "")
        if self.model_name == "":
            raise ModelNotFoundError("Model name not found in environment variables")
        self.client = openai.OpenAI(
            api_key=os.getenv("MODEL_KEY"),
            base_url=os.getenv("MODEL_BASE_URL"),
            http_client=httpx.Client(verify=False),
            max_retries=5,
        )

    def __call__(self,
        system_prompt: str,
        user_prompt: str,
        response_format = None
    ):
        '''
        Returns the response from the LLM.
        If response_format is provided, it returns the parsed response.
        Otherwise, it returns the raw response.
        '''
        chat_completion_params = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.0,
            "max_tokens": 4096,
            "top_p": 1,
        }
        if response_format is not None:
            chat_completion_params['response_format'] = response_format
            response = self.client.beta.chat.completions.parse(**chat_completion_params)
            return response.choices[0].message.parsed

        response = self.client.chat.completions.create(**chat_completion_params)
        if len(response.choices) == 0 or response.choices[0].message.content is None:
            raise NoResponseFromModelError()
        return response.choices[0].message.content
