from typing import Any, List, Optional
from pydantic import BaseModel, Field

from automcp.models import (
    ModelResponse,
    ModelResponseList,
    TasksTag,
    ModelResponseData,
    Command,
    Argument,
    Option,
    CommandItem
)

from automcp.llm.task import LLMTask
from automcp.logger import setup_logging


logger = setup_logging(__name__)


SYS_PROMPT = """Given the man page for a CLI command utility, extract all the commands.

Rules:
- Only extract what is present.
- Return a list of commands.
- Each command should be a string.
- Each command should be a single word.
- Do NOT include description or any other text.
- Do NOT include arguments or options.
- Do NOT include aliases.
"""

USER_PROMPT = """### Query
{query}
"""

class CommandList(BaseModel):
    commands: List[str]

class ExtractCommandList(LLMTask):
    """
    Extracts all the commands from the user query.
    """

    def __init__(
        self,
        query: str,
        tags: List = [],
        metadata: Any = None
    ):
        self._tags = tags
        self.query = query
        self.metadata = metadata

    @property
    def tags(self):
        return [TasksTag.extract_command_list] + self._tags

    def preprocess(self):
        return {
            "query": self.query
        }

    def prompt(self):
        return {
            "system": SYS_PROMPT,
            "user": USER_PROMPT,
            "response_format": CommandList,
        }

    def postprocess(self, result: CommandList) -> ModelResponseList:
        tags = self.tags
        return ModelResponseList(
            items=result.commands,
            tags=tags,
            metadata=self.metadata
        )
