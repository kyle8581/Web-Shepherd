USER_INSTRUCTION = """## User Instruction
{intent}
"""

TRAJECTORY = """## Trajectory
{trajectory}"""

AGENT_RESPONSE = """## Agent's Response
THOUGHT: {thought}
ACTION: {action}
"""

CHECKLIST = """## Checklist
{checklist}
"""


# Observation
CURRENT_URL = """### Current URL
{current_url}
"""

TEXT_OBSERVATION = """### AXTREE
Note: [bid] is the unique alpha-numeric identifier at the beginning of lines for each element in the AXTree. Always use bid to refer to elements in your actions.
{text_observation}
"""

SOM_IMAGE_OBSERVATION = """### SOM Image Screenshot
Here is a current image screenshot of the page, it is annotated with bounding boxes and corresponding bids:
<IMAGE_PLACEHOLDER>
"""

COORD_IMAGE_OBSERVATION = """### Raw Image Screenshot
Here is a screenshot of the page:
<IMAGE_PLACEHOLDER>
"""
