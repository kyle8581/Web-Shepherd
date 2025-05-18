CHECKLIST_SYSTEM_PROMPT = "You are an AI assistant tasked with generating structured checklists that highlight key subgoals necessary to complete a task."

CHECKLIST_USER_PROMPT = """## Task Description
User Instruction (Goal): "{intent}"
Start Website URL: {start_url}

## Guidelines for Checklist Generation
1. Identify Essential High-Level Subgoals:
- A subgoal should represent a significant step involving user interaction that leads to noticeable page transitions or meaningful changes in system state.
- Consolidate closely related user actions (such as applying multiple filters or selecting several options) into a single subgoal, rather than separate checklist items for each action.
- Prioritize only the most critical interactions necessary for meaningful progression, avoiding the inclusion of minor or unnecessary steps (e.g., scroll, hover).
2. Provide a Concise Subgoal Analysis:
- Before creating the checklist, offer a brief paragraph summarizing the main subgoals, emphasizing significant transitions or page-level interactions.
3. Ensure Clear Goal:
- If multiple related interactions occur (e.g., setting filters 1, 2, and 3), combine them into one subgoal with clear criteria verifying all required conditions.
- The checklist should contain only essential steps, explicitly excluding unnecessary actions, and should not exceed five critical subgoals. It is not necessary to use all five checklist items if fewer steps adequately represent the essential subgoals.

### Output Format
Before generating the checklist, first produce a concise subgoal analysis in a single paragraph summarizing the required interactions. Then, based on this, generate the checklist following the format below:
[SUBGOAL ANALYSIS]  
[One-paragraph summary explaining the key subgoals and their logical sequence in task completion.]  

[CHECKLISTS]
Checklist X: [Short title of the action/goal]
- Goal: [Brief description of the subgoal at this stage, emphasizing the purpose of the action.]
"""


CHECKLIST_OURS_USER_PROMPT = """You are an AI assistant tasked with generating structured checklists that highlight key subgoals necessary to complete a task.

# Task Description
Generate a checklist which are key milestones for achieving the given instruction. Frist, provide a concise 
subgoal analysis in a single paragraph summarizing the required interactions. Then, based on this, generate the checklist with breif description.

Note: If the target website requires login, assume the user is already logged in and starts from an authenticated session.

# Given Information
## User Instruction
{intent}

## Current State
### Current URL
{start_url}

### AXTREE
Note: [bid] is the unique alpha-numeric identifier at the beginning of lines for each element in the AXTree. Always use bid to refer to elements in your actions.
{text_observation}
"""