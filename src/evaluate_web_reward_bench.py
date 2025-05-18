import os
import argparse
import logging
import re
from copy import deepcopy
from datasets import load_dataset

from webprm.models import WebPRM, ChecklistGenerationModel
from utils.utils import save_json, load_json, str_to_bool, create_html_report
from utils.eval_utils import processing_results
from utils.inference_utils import run_parallel_evaluation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def evaluate_process(config, data):
    results = deepcopy(data)
    agent_config = config["agent_config"]
    experiment_config = config["experiment_config"]

    # checklist generation
    if experiment_config["evaluation_mode"] == "checklist_generation":
        checklist_generation_model = ChecklistGenerationModel(agent_config)
        checklist_prompt_type = "web_shepherd" if "web_shepherd" in experiment_config["prompt_type"] else "default"
        response, cost = checklist_generation_model.generate_response(data, checklist_prompt_type)

        # add response to results
        if "[CHECKLISTS]" in response[0]:
            results["generated_checklist"] = response[0].split("[CHECKLISTS]")[-1].strip()
        elif "<answer>" in response[0]:
            results["generated_checklist"] = response[0].split("<answer>")[-1].split("</answer>")[0].strip()
        else:
            results["generated_checklist"] = response[0]
    else:
        # get checklist
        if experiment_config["evaluation_mode"] == "judge_with_gt_checklist":
            prompt_type = "web_shepherd" if "web_shepherd" in experiment_config["prompt_type"] else "with_checklist"
            checklist = data["gt_checklist"] 
        elif experiment_config["evaluation_mode"] == "judge_with_checklist_generation":
            prompt_type = "web_shepherd" if "web_shepherd" in experiment_config["prompt_type"] else "with_checklist"
            checklist = data["generated_checklist"]
        else:
            prompt_type = experiment_config["prompt_type"]
            checklist = None
        data["checklist"] = checklist

        # generate response
        webprm = WebPRM(agent_config)
        if experiment_config["use_log_probs"]:
            response, cost = webprm.generate_probs(data, prompt_type)
        else:
            response, cost = webprm.generate_response(data, prompt_type)
        

        # add response to results
        if experiment_config["use_log_probs"]:
            results["response"] = [res["response"] for res in response]
            results["judge_probs"] = [res["judge_probs"] for res in response]
        else:
            results["response"] = response
    
    return results, cost


def setup(args):
    # Create save directory
    os.makedirs(args.save_dir, exist_ok=True)

    # Load dataset
    dataset = load_dataset(args.dataset_name, split="test")
    if args.num_data is not None:
        dataset = dataset.select(range(args.num_data))

    # Judge Agent Config
    agent_config = {
        "model_name": args.model_name,
        "base_url": args.base_url,
        "api_key": args.api_key,
        "temperature": args.temperature,
        "num_generate": args.num_generate,
        "input_type": args.input_type,
        "use_multimodal": False if args.input_type == "text_only" else True,
        "use_log_probs": args.use_log_probs
    }
    experiment_config = {
        "evaluation_mode": args.evaluation_mode,
        "prompt_type": args.prompt_type,
        "use_log_probs": args.use_log_probs
    }
    config = {
        "agent_config": agent_config,
        "experiment_config": experiment_config
    }

    judgement_dataset = setup_for_judgement(dataset, experiment_config)

    return judgement_dataset, config

def setup_for_checklist_generation(data):
    checklist_data = {}
    for item in data:
        if item["task_id"] not in checklist_data:
            checklist_data[item["task_id"]] = {
                "task_id": item["task_id"],
                "intent": item["intent"],
                "start_url": item["start_url"],
                "text_observation": item["text_observation"],   
                "gt_checklist": item["gt_checklist"],
            }
    return list(checklist_data.values())

def get_trajectory(data, step_id, experiment_config):
    trajectory = ""
    if step_id == 0:
        return trajectory
    # get only last 10 steps (you can change this number)
    start_step = max(0, step_id - 10)
    for i in range(start_step, step_id):
        trajectory += f"Thought {i+1}: {data['thought_history'][i]}\nAction {i+1}: {data['action_history'][i]}\n\n"

    return trajectory

def setup_for_judgement(dataset, experiment_config):
    judgement_data = []
    for data in dataset:
        for i, chosen_data in enumerate(data["chosen"]):
            input_info = {
                "task_id": data["task_id"],
                "step_id": data["step_id"],
                "intent": data["intent"],
                "start_url": data["start_url"],
                "trajectory": get_trajectory(data, data["step_id"], experiment_config),
                "current_url": data["current_url"],
                "text_observation": data["text_observation"],
                "thought": chosen_data["thought"],
                "action": chosen_data["action"],
                "image_list": data["image_list"] if "image_list" in data else [],
                "gt_checklist": data["gt_checklist"],
                "type": "chosen",
                "source_name": data["source_name"],
            }
            judgement_data.append(input_info)

        for i, rejected_data in enumerate(data["rejected"]):
            input_info = {  
                "task_id": data["task_id"],
                "step_id": data["step_id"],
                "intent": data["intent"],
                "start_url": data["start_url"],
                "trajectory": get_trajectory(data, data["step_id"], experiment_config),
                "current_url": data["current_url"],
                "text_observation": data["text_observation"],
                "thought": rejected_data["thought"],
                "action": rejected_data["action"],
                "image_list": data["image_list"] if "image_list" in data else [],
                "gt_checklist": data["gt_checklist"],
                "type": "rejected",
                "source_name": data["source_name"],
            }
            judgement_data.append(input_info)


    return judgement_data


def main(args):
    judgement_dataset, config = setup(args)

    n_sample_name = f"{args.num_generate}_samples" if args.num_generate > 1 else "1_sample"
    if args.prompt_type == "likert_scale":
        experiment_name = f"likert_scale_{n_sample_name}"
    elif args.prompt_type == "with_checklist" or args.prompt_type == "web_shepherd":
        if args.evaluation_mode == "judge_with_gt_checklist":
            experiment_name = f"gt_checklist_{n_sample_name}"
        else:
            experiment_name = f"checklist_generation_{n_sample_name}"
    else:
        raise ValueError(f"Invalid prompt type: {args.prompt_type}")
    
    if args.use_log_probs:
        experiment_name += "_probs"

    os.makedirs(args.save_dir, exist_ok=True)
    os.makedirs(os.path.join(args.save_dir, args.save_model_name), exist_ok=True)

    checklist_results = []
    checklist_cost = 0

    # Checklist Generation (if needed)
    if config["experiment_config"]["evaluation_mode"] == "judge_with_checklist_generation":
        checklist_save_path = os.path.join(args.save_dir, args.save_model_name, "checklist.json")

        if os.path.exists(checklist_save_path):
            logger. info(f"Checklist results already exist in {checklist_save_path}")
            checklist_results = load_json(checklist_save_path)
        else:
            logger.info("Current Stage: Generating checklists...")
            checklist_config = deepcopy(config)
            checklist_config["agent_config"]["temperature"] = 0
            checklist_config["agent_config"]["num_generate"] = 1
            checklist_config["experiment_config"]["evaluation_mode"] = "checklist_generation"
            
            checklist_data = setup_for_checklist_generation(judgement_dataset)

            checklist_results, checklist_cost = run_parallel_evaluation(
                dataset=checklist_data,
                process_func=evaluate_process,
                config=checklist_config,
                num_workers=args.num_workers,
                description="Generating Checklists"
            )

            logger.info(f"Checklist generation cost: {checklist_cost:.3f}")
            save_json(checklist_results, checklist_save_path)
            logger.info(f"Checklist results saved to {checklist_save_path}")

        task_checklist_map = {}
        for result in checklist_results:
            task_checklist_map[str(result["task_id"])] = result

        # Add generated checklist to judge_input_data
        for judge_data in judgement_dataset:
            if str(judge_data["task_id"]) in task_checklist_map:
                judge_data["generated_checklist"] = task_checklist_map[str(judge_data["task_id"])]["generated_checklist"]
            else:
                raise ValueError(f"Generated checklist not found for task_id: {judge_data['task_id']}")

    # Judging Stage
    logger.info("Current Stage: Judging responses...")
    judge_config = deepcopy(config)

    total_results, judge_cost = run_parallel_evaluation(
        dataset=judgement_dataset,
        process_func=evaluate_process,
        config=judge_config,
        num_workers=args.num_workers,
        description="Judging Responses"
    )
    logger.info(f"Judge stage cost: {judge_cost:.3f}")
    logger.info(f"Total cost: {checklist_cost + judge_cost:.3f}")
    logger.info("All tasks are finished.")


    # Process and save final results
    final_results, stats = processing_results(total_results, args.evaluation_mode, args.num_generate)
    results_save_path = os.path.join(args.save_dir, args.save_model_name, f"{experiment_name}_results.json")
    save_json(final_results, results_save_path)

    # save html report
    create_html_report(results_save_path, os.path.join(args.save_dir, args.save_model_name, f"{experiment_name}_results.html"), checklist_generation=config["experiment_config"]["evaluation_mode"] == "judge_with_checklist_generation")

    # save stats
    os.makedirs(os.path.join(args.save_dir, args.save_model_name, "stats"), exist_ok=True)
    save_json(stats, os.path.join(args.save_dir, args.save_model_name, "stats", f"{experiment_name}.json"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_name", type=str, default="WebShepherd/WebRewardBench", required=True)
    parser.add_argument("--save_dir", type=str, default="output/WebRewardBench", required=True)
    parser.add_argument("--save_model_name", type=str, default="results.json", required=True)
    # Judge Agent Config
    parser.add_argument("--model_name", type=str, default="gpt-4o-mini", required=True)
    parser.add_argument("--base_url", type=str, default="https://api.openai.com/v1")
    parser.add_argument("--api_key", type=str, required=True)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--num_generate", type=int, default=1)
    # Experiment Config
    parser.add_argument("--evaluation_mode", type=str, default="judge_wo_checklist", choices=["judge_wo_checklist", "judge_with_checklist_generation", "judge_with_gt_checklist"])
    parser.add_argument("--prompt_type", type=str, default="likert_scale", required=True, choices=["likert_scale", "with_checklist", "web_shepherd"])
    parser.add_argument("--input_type", type=str, default="text_only", choices=["text_only", "image_only", "text_image"])
    parser.add_argument("--use_log_probs", type=str_to_bool, default=False)
    # Worker Config
    parser.add_argument("--num_workers", type=int, default=10)
    # Evaluation Config
    parser.add_argument("--num_data", type=int, default=None)

    args = parser.parse_args()

    main(args)


