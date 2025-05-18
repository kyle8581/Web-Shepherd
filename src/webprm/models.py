from abc import ABC, abstractmethod
import time
import math

from langchain_openai import ChatOpenAI

from .prompts import get_messages


MAX_RETRY = 3
RETRY_SLEEP = 5
MODEL_COST_MAPPING = {
    "gpt-4o-mini": {
        "input_token_cost": 0.15,
        "output_token_cost": 0.6
    },
    "gpt-4o": {
        "input_token_cost": 2.5,
        "output_token_cost": 10
    },
}


class Model(ABC):
    @abstractmethod
    def generate_response(self, inputs: dict) -> str:
        pass

class BaseModel(Model):
    def __init__(self, agent_config: dict):
        self.agent_config = agent_config
        self._setup()
    
    def _setup(self):
        use_log_probs = self.agent_config.get("use_log_probs", False)
        if use_log_probs:
            self.llm = ChatOpenAI(
                model=self.agent_config["model_name"], 
                base_url=self.agent_config["base_url"], 
                api_key=self.agent_config["api_key"], 
                temperature=self.agent_config["temperature"],
                timeout=300,
                logprobs=True,
                top_logprobs=10
            )
        else:
            self.llm = ChatOpenAI(
                model=self.agent_config["model_name"], 
                base_url=self.agent_config["base_url"], 
                api_key=self.agent_config["api_key"], 
                temperature=self.agent_config["temperature"],
                timeout=300
            )
        self.temperature = self.agent_config["temperature"]
        self.num_generate = self.agent_config["num_generate"]
        self.use_multimodal = self.agent_config.get("use_multimodal", False)

        # setup cost
        model_cost = MODEL_COST_MAPPING.get(self.agent_config["model_name"], None)
        if model_cost and "api" in self.agent_config["base_url"]:
            self.input_token_cost = model_cost["input_token_cost"]
            self.output_token_cost = model_cost["output_token_cost"]
        else:
            self.input_token_cost = 0.0
            self.output_token_cost = 0.0

    def generate_with_retry(self, model_input, constraint_str_list: list = None):
        total_input_tokens = 0
        total_output_tokens = 0
        if self.temperature == 0:
            response = self.llm.invoke(model_input)
            total_input_tokens += response.response_metadata["token_usage"]["prompt_tokens"]
            total_output_tokens += response.response_metadata["token_usage"]["completion_tokens"]
        else:
            for i in range(MAX_RETRY):
                try:
                    response = self.llm.invoke(model_input)
                    total_input_tokens += response.response_metadata["token_usage"]["prompt_tokens"]
                    total_output_tokens += response.response_metadata["token_usage"]["completion_tokens"]
                    if constraint_str_list:
                        pass_constraint_num = 0
                        for constraint_str in constraint_str_list:
                            if constraint_str in response.content:
                                pass_constraint_num += 1
                        if pass_constraint_num == len(constraint_str_list):
                            break
                        else:
                            print(f"Agent has fomat issue, retry... {i+1}/{MAX_RETRY}")
                    else:
                        break
                except Exception as e:
                    print(f"Agent returned an Error: {e}")
                    response = None
                    time.sleep(RETRY_SLEEP)
        
        cost = self.input_token_cost * total_input_tokens / 1000000 + self.output_token_cost * total_output_tokens / 1000000
        
        if response is None:
            return "", cost
        else:
            return response.content, cost
    
    def prepare_message(self, model_input: dict, prompt_type: str):
        message = []
        return message

    def generate_response(self, model_input: dict, prompt_type: str, constraint_str_list: list = None,):
        total_cost = 0
        response_list = []
        # prepare message
        message = self.prepare_message(model_input, prompt_type)
        # print(message)

        # n sampling
        for i in range(self.num_generate):
            response, cost = self.generate_with_retry(message, constraint_str_list)
            response_list.append(response)
            total_cost += cost
        
        return response_list, total_cost



class WebPRM(BaseModel):
    def __init__(self, agent_config: dict):
        super().__init__(agent_config)
        self._setup()
    
    def prepare_message(self, model_input: dict, prompt_type):
        if self.agent_config["input_type"]=="text_only":
            use_multimodal = False
            text_obs = True
            image_obs = False
        elif self.agent_config["input_type"]=="image_only":
            use_multimodal = True
            text_obs = False
            image_obs = True
        elif self.agent_config["input_type"]=="text_image":
            use_multimodal = True
            text_obs = True
            image_obs = True
        else:
            raise ValueError(f"Invalid input type: {self.agent_config['input_type']}")
        

        message = get_messages(
            input_info=model_input,
            inference_mode="judge_progress",
            prompt_type=prompt_type,
            use_multimodal=use_multimodal,
            text_obs=text_obs,
            image_obs=image_obs,
        )
        return message
    
    def add_to_ori_logprob(self, ori_logprob: float, add_logprob: float):
        if ori_logprob is None:
            return add_logprob
        else:
            ori_prob = math.exp(ori_logprob)
            add_prob = math.exp(add_logprob)
            return math.log(ori_prob + add_prob)
    
    def get_judge_probs(self, logprobs: list):
        # target_judge = {
        #     "yes": [" Yes", "Yes"],
        #     "no": [" No", "No"],
        #     "in": [" In", "In"]
        # }
        target_judge = {
            "yes": [
                " Yes", "ĠYes", "Yes", "ĊYes",
                "Ġyes", "yes", "Ċyes",
                "ĠYES", "YES", "ĊYES",
                "ĠDone", "Done", "ĊDone",
                "ĠCompleted", "Completed", "ĊCompleted",
                "ĠCorrect", "Correct", "ĊCorrect"
            ],
            "no": [
                " No", "ĠNo", "No", "ĊNo",
                "ĠNO", "NO", "ĊNO",
                "ĠNot", "Not", "ĊNot",
                "ĠNone", "None", "ĊNone",
                "ĠNope", "Nope", "ĊNope",
                "ĠUn", "Un", "ĊUn",
                "ĠWrong", "Wrong", "ĊWrong"
            ],
            "in": [
                " In", "ĠIn", "In", "ĊIn",
                "ĠPending", "Pending", "ĊPending",
                "ĠPart", "Part", "ĊPart",
                "ĠPartial", "Partial", "ĊPartial",
                "ĠInProgress", "InProgress", "ĊInProgress"
            ]
        }
        response_str = ""
        judge_probs_list = []
        # print(logprobs)
        for i, log_prob in enumerate(logprobs):
            # Start to find judge string
            if "<answer>" in response_str or "CHECKLIST EVALUATION:" in response_str:
                find_judge_str = None
                for judge_type in target_judge:
                    if log_prob["token"] in target_judge[judge_type]:
                        find_judge_str = judge_type
                        break
                if find_judge_str:
                    token_judge_dict = {
                        "yes": None,
                        "no": None,
                        "in": None
                    }
                    if "top_logprobs" in log_prob:
                        for token_info in log_prob["top_logprobs"]:
                            for judge_type in target_judge:
                                for judge_str in target_judge[judge_type]:
                                    if judge_str in token_info["token"]:
                                        token_judge_dict[judge_type] = self.add_to_ori_logprob(token_judge_dict[judge_type], token_info["logprob"])
                        # for None case
                        for judge_type in token_judge_dict:
                            if token_judge_dict[judge_type] is None:
                                token_judge_dict[judge_type] = float("-inf")
                        judge_probs_list.append(token_judge_dict)
                    else:
                        # for vllm bugs : no top_logprobs
                        for judge_type in token_judge_dict:
                            if judge_type == find_judge_str:
                                token_judge_dict[judge_type] = log_prob["logprob"]
                            else:
                                token_judge_dict[judge_type] = float("-inf")
                        judge_probs_list.append(token_judge_dict)
            
            if "</answer>" in response_str:
                break
            
            response_str += log_prob["token"]

        if len(judge_probs_list) == 0:
            return [{
                "yes": 0.0,
                "no": 0.0,
                "in": 0.0
            }]
        else:
            # convert with softmax
            final_judge_probs_list = []
            for judge_probs in judge_probs_list:
                exp_logprobs = [math.exp(x) for x in [judge_probs["yes"], judge_probs["no"], judge_probs["in"]]]
                sum_exp_logprobs = sum(exp_logprobs)
                softmax_probs = [x / sum_exp_logprobs for x in exp_logprobs]
                final_judge_probs_list.append({
                    "yes": softmax_probs[0], 
                    "no": softmax_probs[1],
                    "in": softmax_probs[2]
                })
            return final_judge_probs_list
    
    def generate_probs(self, model_input: dict, prompt_type: str):
        total_cost = 0
        response_list = []
        # prepare message
        message = self.prepare_message(model_input, prompt_type)

        for i in range(self.num_generate):
            try:
                response = self.llm.invoke(message)
                total_input_tokens = response.response_metadata["token_usage"]["prompt_tokens"]
                total_output_tokens = response.response_metadata["token_usage"]["completion_tokens"]
                total_cost = self.input_token_cost * total_input_tokens / 1000000 + self.output_token_cost * total_output_tokens / 1000000  
                logprobs = response.response_metadata["logprobs"]["content"]
                response_list.append(
                    {
                        "response": response.content,
                        "judge_probs": self.get_judge_probs(logprobs)
                    }
                )
            except Exception as e:
                print(f"Error: {e}")
                response_list.append(
                    {
                        "response": response.content,
                        "judge_probs": []
                    }
                )
        return response_list, total_cost


class ChecklistGenerationModel(BaseModel):
    def __init__(self, agent_config: dict):
        super().__init__(agent_config)
        self._setup()
    
    def prepare_message(self, model_input: dict, prompt_type):
        message = get_messages(
            input_info=model_input,
            inference_mode="checklist_generation",
            prompt_type=prompt_type
        )
        return message