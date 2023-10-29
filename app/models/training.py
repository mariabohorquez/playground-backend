from typing import List, Optional

from beanie import Document, Indexed, Insert, before_event


class DialogueTraining(Document):
    prompt: Indexed(str, unique=True)
    lines: List[str]
    prompt_hash: Optional[str] = None

    @before_event(Insert)
    def compute_prompt_hash(self):
        self.prompt_hash = hash(self.prompt)

    @classmethod
    async def find_by_hash(cls, prompt_hash: str) -> "DialogueTraining":
        """Get a dialogue training by prompt_hash"""
        return await cls.find_one(cls.prompt_hash == prompt_hash)

    class Settings:
        name = "dialogue_training"
