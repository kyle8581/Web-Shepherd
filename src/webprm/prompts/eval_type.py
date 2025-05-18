PROGRESS_LIKERT_SCALE_TASK = """Evaluate how helpful the given thought and action is for achieving the goal. Use the following scale:
**Scoring Criteria (1 to 5):**
- **5 (Very Helpful)**: The action directly and effectively moves toward fulfilling a key part of the goal.
- **4 (Helpful)**: The action contributes meaningfully to progress, though it may require follow-up actions.
- **3 (Somewhat Helpful)**: The action is partially relevant or a preparatory step, but doesn’t make immediate progress.
- **2 (Slightly Helpful)**: The action is weakly related to the goal or might only indirectly help.
- **1 (Not Helpful)**: The action is unrelated, redundant, or distracts from the goal."""

PROGRESS_LIKERT_SCALE_FORMAT = """Please return your response in the following format:
REASON: [Your explanation for the score]
SCORE: [1-5]"""



PROGRESS_WITH_CHECKLIST_IN_PROGRESS_TASK = """Your task is to evaluate how well the agent's THOUGHT and ACTION satisfy each item in the checklist.
Use the task instruction, trajectory (including previously completed steps from history), current webpage state, and the agent's current response as evidence for your evaluation. Clearly consider any items already successfully completed or currently in progress according to the provided trajectory.
For each checklist item:
- Mark it as 'Yes' if it is clearly and fully satisfied either in the current response or already completed in the history.
- Mark it as 'In Progress' if the agent has made partial but meaningful progress toward completing the item.
- Mark it as 'No' if there is ambiguity, insufficient evidence, or the step is incomplete or not yet started."""

PROGRESS_WITH_CHECKLIST_IN_PROGRESS_FORMAT = """Please return your response in the following format:
REASON: [Write a single, coherent paragraph explaining how well the agent's response satisfies the checklist overall. Use both the history and the agent's current thought/action as evidence. Mention specific strengths or missing elements that influence your decision.]
CHECKLIST EVALUATION:  
Checklist X: [Yes / In Progress / No]  
"""


## EVALUATION TYPE
PROGRESS_LIKERT_SCALE = {
    "task_description": PROGRESS_LIKERT_SCALE_TASK,
    "output_format": PROGRESS_LIKERT_SCALE_FORMAT,
}

PROGRESS_WITH_CHECKLIST_IN_PROGRESS = {
    "task_description": PROGRESS_WITH_CHECKLIST_IN_PROGRESS_TASK,
    "output_format": PROGRESS_WITH_CHECKLIST_IN_PROGRESS_FORMAT,
}