import json
import os
from openai import OpenAI
from app.logger import get_logger
from dotenv import load_dotenv

load_dotenv()

class GPT:
    def __init__(self, prompt_path="prompts/generate_comment.txt"):
        self.log = get_logger("openai")
        self.openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEYS'))
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.prompt_template = f.read()
    
    def generate_comment(self, content: str):
        self.log.info("댓글 생성 중...")
        prompt = self.prompt_template.format(content=content)
        
        response = self.openai_client.chat.completions.create(
            model=os.environ.get('OPENAI_MODEL'),
            messages=[
                {'role': 'user', 'content': prompt}
            ]
        )
        self.log.debug(f"prompt {response.usage.prompt_tokens} tokens, completion {response.usage.completion_tokens} tokens: 총 {response.usage.total_tokens} tokens 사용")
        comment_json = response.choices[0].message.content
        
        try:
            return json.loads(comment_json)["comment"]
        except (json.JSONDecodeError, KeyError) as e:
            self.log.error(f"OpenAI 응답 파싱 실패: {e}")
            self.log.error(f"원본 응답: {comment_json}")
            return "😊" # 기본 댓글
