import json
import os
from openai import OpenAI
from app.logger import get_logger
from dotenv import load_dotenv

load_dotenv()
class GPT():
    def __init__(self):
        self.log = get_logger("openai")
        self.openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEYS'))
    
    def generate_comment(self, content: str):
        self.log.info("댓글 생성 중...")
        prompt = f"""
            아래 게시글에 대해서 특수문자를 사용하지 않고 한글 또는 이모지로만 이루어진 댓글을 친한 친구에게 이야기 하듯이 작성해줘.
            
            ```
            {content}
            ```

            요구사항:
            1. json형식에 맞게 줄바꿈은 하지말고 한 줄로 응답해줘.
            2. `comment`필드에 `댓글`을 줘.
            """
        
        response = self.openai_client.chat.completions.create(
            model=os.environ.get('OPENAI_MODEL'),
            messages=[
                {'role': 'user', 'content': prompt}
            ]
        )
        self.log.debug(f"prompt {response.usage.prompt_tokens} tokens, completion {response.usage.completion_tokens} tokens: 총 {response.usage.total_tokens} tokens 사용")
        comment_json = response.choices[0].message.content
        return json.loads(comment_json)["comment"]