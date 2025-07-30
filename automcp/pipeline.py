from automcp.llm.executor import LLMTaskExecutor
from typing import List, Tuple, cast
from automcp.llm.tasks.extract_command import Command, ExtractCommand
from automcp.models import (
    COMMAND_HELP,
    CommandItem,
    ModelBooleanResponse,
    ModelResponseData,
    ModelResponseList,
)
from automcp.logger import setup_logging
from automcp.utils import run_shell
from automcp.llm.tasks.detect_sub_commands import DetectSubCommands
from automcp.templates.generator import create_server_template
from automcp.llm.tasks.extract_command_list import ExtractCommandList

logger = setup_logging(__name__)


class AutoMCP_Pipeline:
    def __init__(self):
        self.executor = LLMTaskExecutor()

    def run(self, program: List[str] | str, help_command: str):
        '''Run the pipeline for a given program to generate MCP server.'''
        if isinstance(program, str):
            program = [program]
        sub_commands = []
        for p in program:
            sub_commands += self._detect_sub_commands(p, help_command)
        logger.debug("No. of sub-commands: %d", len(sub_commands))

        server_template = create_server_template(sub_commands)
        # logger.debug("Server template: %s", server_template)

        return server_template

    def _detect_sub_commands(self, program: str, help_command: str):
        '''Recursively detect sub-commands from the help docs.'''
        help_docs = run_shell(
            COMMAND_HELP.format(program=program, help_command=help_command)
        )
        logger.debug("Length of help docs: %d", len(help_docs))
        # logger.debug("First 100 chars of help docs: %s", help_docs[:100] + "...")

        if self.check_sub_command_exists(program, help_docs):
            command_list = self.extract_command_list(help_docs)
            logger.debug("Found %d commands", len(command_list))
            
            if not self.validate_command_list(command_list, program):
                return []

            logger.debug("\nExtracted commands:")
            for command in command_list:
                logger.debug("  %s", command)
            result = []
            for command in command_list:
                result += self._detect_sub_commands(f"{program} {command}", help_command)
            return result
        else:
            try:
                return [self.extract_command(program, help_docs)]
            except Exception as e:
                logger.error("Error extracting command (%s): %s", program, e)
                return []

    def check_sub_command_exists(self, program: str, help_docs: str):
        '''Check if the help docs contain sub-commands.'''
        result = self.executor.run(
            DetectSubCommands(
                query=help_docs,
                command=program
            )
        )
        result = cast(ModelBooleanResponse, result)
        return result.bool_value

    def extract_command(self, command: str, help_docs: str) -> CommandItem:
        '''Extract the command from the help docs.'''
        result = self.executor.run(
            ExtractCommand(query=help_docs, command=command)
        )
        result = cast(ModelResponseData, result)
        data = cast(Command, result.data)
        logger.debug("Extracted options: %s", data.options)
        return CommandItem(command=command, data=data)

    def extract_command_list(self, help_docs: str) -> List[str]:
        '''Extract all the commands from the help docs.'''
        result = self.executor.run(
            ExtractCommandList(query=help_docs)
        )
        result = cast(ModelResponseList, result)
        return cast(List[str], result.items)
    
    def validate_command_list(self, command_list: List[str], program: str) -> bool:
        '''Validate the command list.'''
        if " ".join(command_list) == program:
            return False
        if len(set(command_list)) != len(command_list):
            return False
        return True
