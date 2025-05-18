import json
import base64
import io
import html
from PIL import Image


def image_to_base64_url(image: str | Image.Image):
    if isinstance(image, str):
        with open(image, "rb") as f:
            image = f.read()
    elif isinstance(image, Image.Image):
        if image.mode in ("RGBA", "LA"):
            image = image.convert("RGB")
        with io.BytesIO() as buffer:
            image.save(buffer, format="PNG")
            image = buffer.getvalue()
    else:
        raise ValueError(f"Invalid image type: {type(image)}")
    
    return "data:image/png;base64," + base64.b64encode(image).decode("utf-8")


def load_json(file_path: str) -> dict:
    with open(file_path, "r") as f:
        return json.load(f)
    
def save_json(data: dict, file_path: str):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def str_to_bool(s: str) -> bool:
    if s.lower() in ["true", "1", "yes", "y"]:
        return True
    elif s.lower() in ["false", "0", "no", "n"]:
        return False
    else:
        raise ValueError(f"Invalid boolean string: {s}")
    

def create_html_report(json_path, html_path, checklist_generation=False):
    """
    Reads the given JSON result file and generates a filterable HTML report.

    Args:
        json_path (str): Path to the input JSON file.
        html_path (str): Path to the output HTML file.
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file not found - {json_path}") # Error message in English
        return
    except json.JSONDecodeError:
        print(f"Error: JSON file parsing error - {json_path}") # Error message in English
        return
    except Exception as e:
        print(f"Unexpected error during data loading: {e}") # Error message in English
        return

    # Extract unique Task IDs and sort them
    task_ids = sorted(list(set(item.get("task_id") for item in data if item.get("task_id") is not None)))

    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Benchmark Results Report</title>
    <style>
        body { font-family: sans-serif; line-height: 1.6; padding: 20px; }
        .task-step { border: 1px solid #ccc; margin-bottom: 20px; padding: 15px; border-radius: 5px; background-color: #f9f9f9; }
        .task-step h2 { margin-top: 0; color: #333; border-bottom: 1px solid #eee; padding-bottom: 5px;}
        .task-step h3 { color: #555; margin-top: 15px; margin-bottom: 5px; }
        .task-step h4 { color: #777; margin-top: 10px; margin-bottom: 5px; font-style: italic;}
        pre { background-color: #eee; padding: 10px; border-radius: 3px; white-space: pre-wrap; word-wrap: break-word; font-size: 0.9em; margin-top: 5px; }
        details { margin-top: 10px; border: 1px solid #ddd; border-radius: 3px; background-color: #fff; }
        summary { cursor: pointer; padding: 8px; background-color: #f8f9fa; font-weight: bold; border-bottom: 1px solid #ddd; }
        details[open] summary { border-bottom: 1px solid #ddd; }
        details > pre { border: none; background-color: #fff; padding: 10px 8px; }
        .response-item-toggle { margin-top: 10px; }
        .chosen-section { border-left: 5px solid #4CAF50; padding-left: 10px; margin-top: 15px; }
        .rejected-section { border-left: 5px solid #f44336; padding-left: 10px; margin-top: 15px; }
        hr { border: 0; border-top: 1px solid #eee; margin: 15px 0; }
        .thought-action { background-color: #f0f0f0; padding: 10px; border-radius: 3px; margin-bottom: 10px; border: 1px solid #e0e0e0;}
        .thought-action h4 { margin-top: 0; color: #666; }
        .task-container { display: none; }
        .filter-controls { margin-bottom: 20px; padding: 10px; background-color: #e9ecef; border-radius: 5px; }
        .filter-controls label { margin-right: 10px; font-weight: bold; }
        .filter-controls select { padding: 5px; border-radius: 3px; border: 1px solid #ced4da; }
    </style>
</head>
<body>
    <h1>Benchmark Results Report</h1>

    <!-- Task ID Filter Dropdown -->
    <div class="filter-controls">
        <label for="taskSelector">Select Task ID:</label>
        <select id="taskSelector">
            <option value="">-- Show All --</option>
"""
    # Add dropdown options
    for tid in task_ids:
        html_content += f'            <option value="{html.escape(str(tid))}">{html.escape(str(tid))}</option>\n'

    html_content += """
        </select>
    </div>

    <!-- Results Display Area -->
    <div id="resultsArea">
"""

    # Process each Task/Step data
    for i, step_data in enumerate(data):
        task_id = step_data.get("task_id", "N/A")
        step_id = step_data.get("step_id", "N/A")
        intent = step_data.get("intent", "N/A")
        start_url = step_data.get("start_url", "N/A")
        gt_checklist = step_data.get("gt_checklist", "N/A")
        generated_checklist = step_data.get("generated_checklist", None)
        trajectory = step_data.get("trajectory", "N/A")
        text_observation = step_data.get("text_observation", "N/A")
        source_name = step_data.get("source_name", "")

        # Wrap each Task/Step in a container with a unique ID (hidden initially)
        html_content += f"""
    <div class="task-container" data-task-id="{html.escape(str(task_id))}">
        <div class="task-step">
            <h2>Task ID: {html.escape(str(task_id))} | Step ID: {html.escape(str(step_id))} {f'({html.escape(source_name)})' if source_name else ''}</h2>
            <h3>Intent:</h3>
            <p>{html.escape(intent)}</p>
            <p><strong>Start URL:</strong> <a href="{html.escape(start_url)}" target="_blank">{html.escape(start_url)}</a></p>

            <h3>Ground Truth Checklist:</h3>
            <pre>{html.escape(gt_checklist)}</pre>
"""
        if checklist_generation and generated_checklist is not None:
            html_content += f"""
            <details>
                <summary>Generated Checklist (Click to expand/collapse)</summary>
                <pre>{html.escape(str(generated_checklist))}</pre>
            </details>
"""

        html_content += f"""
            <details>
                <summary>Trajectory (Click to expand/collapse)</summary>
                <pre>{html.escape(trajectory)}</pre>
            </details>

            <details>
                <summary>Text Observation (Click to expand/collapse)</summary>
                <pre>{html.escape(text_observation)}</pre>
            </details>
            <hr>
"""

        # Chosen Responses
        if 'chosen' in step_data and step_data['chosen']:
            html_content += '<div class="chosen-section"><h3>Chosen Responses:</h3>'
            for choice_block in step_data['chosen']:
                thought = choice_block.get('thought', 'N/A')
                action = choice_block.get('action', 'N/A')
                responses = choice_block.get('response', [])
                scores = choice_block.get('score', [])

                # Add Thought and Action information
                html_content += f"""
            <div class="thought-action">
                <h4>Thought:</h4>
                <pre>{html.escape(thought)}</pre>
                <h4>Action:</h4>
                <pre>{html.escape(action)}</pre>
            </div>"""

                # Loop through responses and create toggles
                for idx, (response, score) in enumerate(zip(responses, scores)):
                     html_content += f"""
            <details class="response-item-toggle">
                <summary>Judge Response {idx + 1}: {html.escape(str(score))}</summary>
                <pre>{html.escape(str(response))}</pre>
            </details>"""
            html_content += '</div>' # End chosen-section

        # Rejected Responses
        if 'rejected' in step_data and step_data['rejected']:
            html_content += '<div class="rejected-section"><h3>Rejected Responses:</h3>'
            for rejection_block in step_data['rejected']:
                thought = rejection_block.get('thought', 'N/A')
                action = rejection_block.get('action', 'N/A')
                responses = rejection_block.get('response', [])
                scores = rejection_block.get('score', [])

                # Add Thought and Action information
                html_content += f"""
            <div class="thought-action">
                <h4>Thought:</h4>
                <pre>{html.escape(thought)}</pre>
                <h4>Action:</h4>
                <pre>{html.escape(action)}</pre>
            </div>"""

                # Loop through responses and create toggles
                for idx, (response, score) in enumerate(zip(responses, scores)):
                     html_content += f"""
            <details class="response-item-toggle">
                <summary>Judge Response {idx + 1}: {html.escape(str(score))}</summary>
                <pre>{html.escape(str(response))}</pre>
            </details>"""
            html_content += '</div>' # End rejected-section

        html_content += """
        </div> <!-- End task-step -->
    </div> <!-- End task-container -->
"""

    # Finalize HTML and add JavaScript
    html_content += """
    </div> <!-- End resultsArea -->

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const taskSelector = document.getElementById('taskSelector');
            const taskContainers = document.querySelectorAll('.task-container');

            function filterTasks() {
                const selectedTaskId = taskSelector.value;

                taskContainers.forEach(container => {
                    const containerTaskId = container.getAttribute('data-task-id');
                    // Show if no Task ID is selected (Show All) or if the container's Task ID matches
                    if (selectedTaskId === "" || containerTaskId === selectedTaskId) {
                        container.style.display = 'block';
                    } else {
                        // Otherwise, hide it
                        container.style.display = 'none';
                    }
                });
            }

            // Run filter function on dropdown change
            taskSelector.addEventListener('change', filterTasks);

            // Run initial filtering on page load (default: Show All)
            filterTasks();
        });
    </script>

</body>
</html>
"""

    # Save the HTML file
    try:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Completed: HTML report created at {html_path}")
    except IOError:
        print(f"Error: Failed to write HTML file - {html_path}")
    except Exception as e:
        print(f"Unexpected error during HTML file saving: {e}")

# --- Example Usage ---
# input_json_file = 'path/to/your/results.json'
# output_html_file = 'trajectory_report.html'
# create_html_report(input_json_file, output_html_file)