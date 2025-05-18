# SYSTEM PROMPT
DEFAULT_SYSTEM_PROMPT_FORMAT = "You are an expert evaluator of web agent. {role_description}"

PROGRESS_WITHOUT_CHECKLIST_ROLE = "Your task is to assess how helpful a given agent's THOUGHT and ACTION is in making progress toward the user's goal, based on the current state of the webpage."
PROGRESS_WITH_CHECKLIST_ROLE = "Your task is to assess how helpful a given agent's THOUGHT and ACTION is in making progress toward the user's goal, based on the current state of the webpage."

# USER PROMPT
DEFAULT_USER_PROMPT_FORMAT = """# Action space:
{action_space}

# Task Description
{task_description}

# Given Information
{input_information}

# Output Format
{output_format}
"""



JUDGE_OURS_USER_PROMPT_FORMAT = """You are an expert evaluator of web agent. Your task is to assess how helpful a given agent's THOUGHT and ACTION is in making progress toward the user's goal, based on the current state of the webpage.

# Task Description
Evaluate how well the agent’s THOUGHT and ACTION satisfy each item in the checklist using the task instruction, trajectory (including previously completed steps), current webpage state, and the agent’s latest response. Start by writing a concise paragraph summarizing the agent’s overall performance. Refer to the reasoning provided in the trajectory, and discuss whether the THOUGHT is appropriate and the ACTION moves the task forward.
Then, assess each checklist item individually using the following labels:
- Yes: The item is fully and clearly satisfied, either in the current response or previously completed.
- In Progress: There is meaningful partial progress toward completing the item.
- No: The item is not satisfied due to ambiguity, insufficient evidence, or lack of progress.

# Given Information
{input_information}
"""


JUDGE_OURS_IMAGE_INPUT = """
### Image Screenshot
<IMAGE_PLACEHOLDER>
"""

JUDGE_OURS_WITH_CHECKLIST = """
## Checklist
{checklist}
"""

BT_MODELING_RESPONSE_FORMAT = """
THOUGHT: {thought}
ACTION: {action}
"""

## PROMPT TEMPLATEß
JUDGE_LIKERT_SCALE_PROMPT_TEMPLATE = {
    "system": DEFAULT_SYSTEM_PROMPT_FORMAT.format(role_description=PROGRESS_WITHOUT_CHECKLIST_ROLE),
    "user": DEFAULT_USER_PROMPT_FORMAT
}

JUDGE_WITH_CHECKLIST_PROMPT_TEMPLATE = {
    "system": DEFAULT_SYSTEM_PROMPT_FORMAT.format(role_description=PROGRESS_WITH_CHECKLIST_ROLE),
    "user": DEFAULT_USER_PROMPT_FORMAT
}

JUDGE_OURS_PROMPT_TEMPLATE = {
    "system": "",
    "user": JUDGE_OURS_USER_PROMPT_FORMAT,
}
