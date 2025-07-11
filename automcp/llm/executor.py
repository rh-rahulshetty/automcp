from typing import List
import concurrent.futures

from automcp.models import (
    DUMMY_PROMPT,
    DUMMY_PROMPT_TOKEN,
    ModelResponse
)

from automcp.llm.task import LLMTask
from automcp.logger import setup_logging
from automcp.llm.client import LLMClient


MAX_WORKERS = 20

logger = setup_logging(__name__)


class LLMTaskExecutor:
    def __init__(self):
        # Lists to track tasks
        self.tasks: List[LLMTask] = []
        self.results: List[ModelResponse] = []

    def __len__(self):
        # Return length of task stack
        return len(self.tasks)

    def add_task(self, task: LLMTask):
        self.tasks.append(task)

    def clear(self):
        self.tasks = []
        self.results = []

    def run(self, task: LLMTask) -> ModelResponse:
        # Parameters passed in from user
        query_params = task.preprocess()

        # System and User prompt for the task
        task_prompts = task.prompt()

        # Prompt passed to LLM
        request_prompt = DUMMY_PROMPT.format(
            system=task_prompts["system"],
            user=task_prompts["user"],
        )

        request_prompt = request_prompt.format(
            **query_params
        )

        sys_prompt, user_prompt = request_prompt.split(DUMMY_PROMPT_TOKEN)

        # logger.debug("System Prompt: %s", sys_prompt)
        # logger.debug("User Prompt: %s", user_prompt[:100] + "...")

        # Initialize LLM Client
        llm_client = LLMClient()

        # Run LLM Prompt
        response = llm_client(
            system_prompt=sys_prompt,
            user_prompt=user_prompt,
            response_format=task_prompts.get("response_format", None),
        )

        logger.debug("LLM Response: %s", response)

        model_response = task.postprocess(
            response
        )

        return model_response

    def run_tasks(self, max_workers=MAX_WORKERS, update_progress_cb=None):
        '''
        Starts running available tasks concurrently with MAX_WORKERS(20) tasks running at a time.
        Additionally you can pass a callback function 'update_progress_cb' to update progress in UI.
        '''
        if len(self.tasks) == 0:
            logger.info("No tasks found to execute!")
            return

        futures = []  # Store promises for task

        with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
            while len(self.tasks) != 0:
                task = self.tasks.pop()
                future = executor.submit(
                    self.run, task=task
                )
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                model_response = future.result()
                self.results.append(model_response)

                if update_progress_cb is not None and callable(update_progress_cb):
                    completed = len(self.results)
                    pending = len(self.tasks)
                    update_progress_cb(completed / (completed + pending))

    def fetch_results(self, search_tags: List[str] = []) -> List[ModelResponse]:
        '''Fetch results from model runs.'''
        if len(search_tags) == 0:
            return self.results

        # Filter results list which matches the tags
        results = []

        for model_response in self.results:
            result_tags = model_response.tags
            # If search tags are available in result tags then add it to response ot result
            a = set(search_tags)
            b = set(result_tags)
            if a & b == a:
                results.append(model_response)

        return results
