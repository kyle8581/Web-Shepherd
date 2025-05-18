from abc import ABC, abstractmethod

from .action import ACTION_SPACE_PROMPT
from .eval_type import (
    PROGRESS_LIKERT_SCALE,
    PROGRESS_WITH_CHECKLIST_IN_PROGRESS,
)
from .input_information import (
    USER_INSTRUCTION,
    TRAJECTORY,
    AGENT_RESPONSE,
    CHECKLIST,
    CURRENT_URL,
    TEXT_OBSERVATION,
    SOM_IMAGE_OBSERVATION, 
)
from .judge_prompt import (
    JUDGE_LIKERT_SCALE_PROMPT_TEMPLATE,
    JUDGE_WITH_CHECKLIST_PROMPT_TEMPLATE,
    JUDGE_OURS_PROMPT_TEMPLATE,
)
from .checklist_prompt import (
    CHECKLIST_SYSTEM_PROMPT,
    CHECKLIST_USER_PROMPT,
    CHECKLIST_OURS_USER_PROMPT
)
from .image_utils import image_to_base64_url


class Message(ABC):    
    @abstractmethod
    def get_messages(self):
        pass

class BaseMessage(Message):
    def __init__(self, input_info:dict, use_multimodal:bool=False):
        self.input_info = input_info
        self.use_multimodal = use_multimodal

    def _get_system_message(self):
        system_message = {"role": "system", "content": "You are a helpful assistant."}
        return system_message
    
    def _process_multimodal_message(self, prompt: str, image_list: list[str]):
        multimodal_message = []
        text_prompt_prefix = prompt.split("<IMAGE_PLACEHOLDER>")[0]
        text_prompt_suffix = prompt.split("<IMAGE_PLACEHOLDER>")[1]
        multimodal_message.append({"type": "text", "text": text_prompt_prefix})
        for i, image in enumerate(image_list):
            multimodal_message.append({"type": "image_url", "image_url": {"url": image_to_base64_url(image), "detail": "low"}})
        multimodal_message.append({"type": "text", "text": text_prompt_suffix})
        return {"role": "user", "content": multimodal_message}
    
    def _get_user_message(self):
        user_prompt = "What is the capital of France?"
        if self.use_multimodal:
            image_list = self.input_info.get("image_list", [])
            user_message = self._process_multimodal_message(user_prompt, image_list)
        else:
            user_message = {"role": "user", "content": user_prompt}
        return user_message

    def get_messages(self):
        message = []
        system_message = self._get_system_message()
        user_message = self._get_user_message()

        message.append(system_message)
        message.append(user_message)
        return message
    

class ProgressMessage(BaseMessage):
    '''
    Progress Judge Message
    '''
    def __init__(self, input_info:dict, use_multimodal:bool, prompt_type:str, text_obs: str, image_obs: str):
        super().__init__(input_info, use_multimodal)
        self.prompt_type = prompt_type
        self.text_obs = text_obs
        self.image_obs = image_obs
        if self.prompt_type == "likert_scale":
            self.use_checklist = False
        else:
            self.use_checklist = True
    
    def _get_system_message(self):
        if self.prompt_type == "likert_scale":
            system_message = {"role": "system", "content": JUDGE_LIKERT_SCALE_PROMPT_TEMPLATE["system"]}
        elif self.prompt_type == "with_checklist":
            system_message = {"role": "system", "content": JUDGE_WITH_CHECKLIST_PROMPT_TEMPLATE["system"]}
        elif self.prompt_type == "web_shepherd":
            system_message = {"role": "system", "content": JUDGE_OURS_PROMPT_TEMPLATE["system"]}
        else:
            raise ValueError(f"Invalid prompt type: {self.prompt_type}")
        return system_message
        
    def _setup_input_information(self):
        observation = "## Current State\n"

        observation += CURRENT_URL

        # text observation
        if self.text_obs:
            observation += TEXT_OBSERVATION
        
        # image observation
        if self.image_obs:
            observation += SOM_IMAGE_OBSERVATION


        if self.use_checklist:
            input_information = USER_INSTRUCTION + TRAJECTORY + observation + CHECKLIST + AGENT_RESPONSE
        else:
            input_information = USER_INSTRUCTION + TRAJECTORY + observation + AGENT_RESPONSE

        return input_information
    
    def _setup_task_info(self):
        if self.prompt_type == "likert_scale":
            task_description = PROGRESS_LIKERT_SCALE["task_description"]
            output_format = PROGRESS_LIKERT_SCALE["output_format"]
        elif self.prompt_type == "with_checklist":
            task_description = PROGRESS_WITH_CHECKLIST_IN_PROGRESS["task_description"]
            output_format = PROGRESS_WITH_CHECKLIST_IN_PROGRESS["output_format"]
        else:
            raise ValueError(f"Invalid prompt type: {self.prompt_type}")
        return task_description, output_format
    
    def _get_user_prompt_template(self):
        if self.prompt_type == "likert_scale":
            user_prompt = JUDGE_LIKERT_SCALE_PROMPT_TEMPLATE["user"]
        elif self.prompt_type == "with_checklist":
            user_prompt = JUDGE_WITH_CHECKLIST_PROMPT_TEMPLATE["user"]
        else:
            raise ValueError(f"Invalid prompt type: {self.prompt_type}")
        return user_prompt
    
    def _get_user_message(self):
        # setup input information (user_instruction, trajectory, current_state, agent_response, checklist)
        input_information_template = self._setup_input_information()
        input_information = input_information_template.format(**self.input_info)

        if self.prompt_type == "web_shepherd":
            user_prompt = JUDGE_OURS_PROMPT_TEMPLATE["user"].format(
                input_information=input_information,
            )
        else:
            task_description, output_format = self._setup_task_info()
            # get user prompt template by prompt type
            user_prompt_template = self._get_user_prompt_template()
            user_prompt = user_prompt_template.format(
                action_space=ACTION_SPACE_PROMPT,
                task_description=task_description,
                input_information=input_information,
                output_format=output_format
            )

        # process multimodal message
        if self.use_multimodal:
            image_list = self.input_info.get("image_list", [])
            user_message = self._process_multimodal_message(user_prompt, image_list)
        else:
            user_message = {"role": "user", "content": user_prompt}

        return user_message


class ChecklistMessage(BaseMessage):
    '''
    Checklist Message
    '''
    def __init__(self, input_info:dict, use_multimodal:bool, prompt_type:str):
        super().__init__(input_info, use_multimodal)
        self.prompt_type = prompt_type
    
    def _get_system_message(self):
        if self.prompt_type == "web_shepherd":
            system_message = {"role": "system", "content": ""}
        elif self.prompt_type == "default":
            system_message = {"role": "system", "content": CHECKLIST_SYSTEM_PROMPT}
        else:
            raise ValueError(f"Invalid prompt type: {self.prompt_type}")
        return system_message
    
    def _get_user_message(self):
        if self.prompt_type == "web_shepherd":
            user_message = {"role": "user", "content": CHECKLIST_OURS_USER_PROMPT.format(**self.input_info)}
        elif self.prompt_type == "default":
            user_message = {"role": "user", "content": CHECKLIST_USER_PROMPT.format(**self.input_info)}
        else:
            raise ValueError(f"Invalid prompt type: {self.prompt_type}")
        return user_message
    


def get_messages(input_info:dict, inference_mode:str, prompt_type:str, text_obs:str=None, image_obs:str=None, use_multimodal:bool=False):
    message_list = []
    if inference_mode == "judge_progress":
        message = ProgressMessage(input_info, use_multimodal=use_multimodal, prompt_type=prompt_type, text_obs=text_obs, image_obs=image_obs)
    elif inference_mode == "checklist_generation":
        message = ChecklistMessage(input_info, use_multimodal=False, prompt_type=prompt_type)
    else:
        raise ValueError(f"Invalid inference mode: {inference_mode}")
    
    system_message, user_message = message.get_messages()
    
    message_list.append(system_message)
    message_list.append(user_message)
    return message_list