import re
import random
from collections import Counter

from .utils import load_json, save_json, create_html_report

random.seed(42)
def get_score(response_list: list, indicator: str) -> int:
    if len(response_list) == 0:
        return [-100]

    if isinstance(response_list[0], float):
        return response_list
    
    if indicator == "prob":
        score_list = []
        for response in response_list:
            total_score = 0
            for judge_probs in response:
                yes_prob = judge_probs.get("yes", 0)
                in_progress_prob = judge_probs.get("in", 0)
                total_score += yes_prob + in_progress_prob * 0.5
            if len(response) > 0:
                score_list.append(total_score / len(response))
            else:
                score_list.append(0)
        return score_list
    else:
        score_list = []
        for response in response_list:
            if indicator == "SCORE":
                if "SCORE" in response:
                    try:
                        score_str = response.split("SCORE:")[1].split("\n")[0].strip()
                    except:
                        score_str = response.split("SCORE:")[-1].strip()
                    # find first integer
                    try:
                        score = re.search(r'-?\d+', score_str).group()
                        score_list.append(int(score))
                    except:
                        score_list.append(0)
                else:
                    try:
                        score_str = response.split("<answer>")[1].split("</answer>")[0].strip()
                    except:
                        score_str = response.split("<answer>")[-1].split("</answer>")[0].strip()
                    # find "Yes" or "No"
                    if "Yes" in score_str:
                        score_list.append(1)
                    elif "In Progress" in score_str:
                        score_list.append(0.5)
                    elif "No" in score_str:
                        score_list.append(0)
                    else:
                        score_list.append(0)
            elif indicator == "JUDGE":
                try:
                    judge_str = response.split("JUDGE:")[1].split("\n")[0].strip()
                except:
                    judge_str = response.split("JUDGE:")[-1].strip()
                if "Yes" in judge_str:
                    score_list.append(1)
                elif "No" in judge_str:
                    score_list.append(0)
                else:
                    score_list.append(0)
            elif indicator == "CHECKLIST EVALUATION":
                if "<answer>" in response:
                    try:
                        checklist_str = response.split("<answer>")[1].split("</answer>")[0].strip()
                    except:
                        checklist_str = response.split("<answer>")[-1].split("</answer>")[0].strip()
                else:
                    checklist_str = response.split("CHECKLIST EVALUATION:")[-1].strip()
                
                count_yes = checklist_str.count("Yes")
                count_no = checklist_str.count("No")
                count_in_progress = checklist_str.count("In Progress")
                try:
                    total_score = (count_yes + count_in_progress*0.5) / (count_yes + count_no + count_in_progress)
                except:
                    total_score = 0
                score_list.append(total_score)
            else:
                raise ValueError(f"Invalid indicator: {indicator}")
    return score_list

def get_acc_and_mrr(chosen_score, rejected_scores):
    if len(rejected_scores) == 0:
        return 0, False
    
    same_score_num = rejected_scores.count(chosen_score)
    all_scores = rejected_scores + [chosen_score]
    sorted_scores = sorted(all_scores, reverse=True)
    rank = sorted_scores.index(chosen_score) + 1 + same_score_num  # draw penalty
    if all(chosen_score > r for r in rejected_scores):
        accuracy = True
    else:
        accuracy = False
    return 1 / rank, accuracy

def average_score(score_list: list[float]):
    if len(score_list) == 0:
        return -100
    return sum(score_list) / len(score_list)

def self_consistency_score(score_list: list[float]):
    if len(score_list) == 0:
        return -100
    counter = Counter(score_list)
    return max(counter.values()) / len(score_list)

def get_chosen_rejected_scores(data: dict, agg_func: str):
    if len(data["chosen"]) == 0:
        data["chosen"] = [{"score": [-100]}]
    if len(data["rejected"]) == 0:
        data["rejected"] = [{"score": [-100]}]
    if not isinstance(data["chosen"][0], dict):
        data["chosen"][0]["score"] = [-100]
    if not isinstance(data["rejected"][0], dict):
        data["rejected"][0]["score"] = [-100]
        
    if agg_func == "average":
        chosen_score = average_score(data["chosen"][0]["score"])
        rejected_scores = [average_score(rejected_score["score"]) for rejected_score in data["rejected"]]
    elif agg_func == "self_consistency":
        chosen_score = self_consistency_score(data["chosen"][0]["score"])
        rejected_scores = [self_consistency_score(rejected_score["score"]) for rejected_score in data["rejected"]]
    else:
        raise ValueError(f"Invalid agg_func: {agg_func}")
    return chosen_score, rejected_scores

def get_score_results(results, agg_func):
    score_dict = {"mrr": [], "accuracy": [], "traj_accuracy": []}
    task_accuracy = {}
    for result in results:
        chosen_score, rejected_scores = get_chosen_rejected_scores(result, agg_func)
        mrr, accuracy = get_acc_and_mrr(chosen_score, rejected_scores)
        score_dict["mrr"].append(mrr)
        score_dict["accuracy"].append(accuracy)
        if result["task_id"] not in task_accuracy:
            task_accuracy[result["task_id"]] = []
        task_accuracy[result["task_id"]].append(accuracy)

    for task_id in task_accuracy:
        if sum(task_accuracy[task_id]) == len(task_accuracy[task_id]):
            score_dict["traj_accuracy"].append(True)
        else:
            score_dict["traj_accuracy"].append(False)

    return score_dict

def calculate_stats(results, agg_func: str="average"):
    if len(results) == 0:
        return {
            "MRR": 0,
            "Accuracy": 0,
            "Traj_Accuracy": 0,
        }
    total_score = get_score_results(results, agg_func)
    stats = {
        "MRR": sum(total_score["mrr"]) / len(total_score["mrr"]),
        "Accuracy": sum(total_score["accuracy"]) / len(total_score["accuracy"]),
        "Traj_Accuracy": sum(total_score["traj_accuracy"]) / len(total_score["traj_accuracy"]),
    }
    
    return stats

def group_by_task(results, split_indicator: str):
    # sort results by task_id and step_id
    results.sort(key=lambda x: (x["task_id"], x["step_id"]))
    # group by task_name
    grouped_task_dict = {}
    for result in results:
        task_name = "task_" + str(result["task_id"]) + "_step_" + str(result["step_id"])
        if task_name not in grouped_task_dict:
            grouped_task_dict[task_name] = {
                "task_id": result["task_id"],
                "step_id": result["step_id"],
                "intent": result["intent"],
                "start_url": result["start_url"],
                "gt_checklist": result["gt_checklist"],
                "generated_checklist": result.get("generated_checklist", None)  ,
                "trajectory": result["trajectory"],
                "current_url": result["current_url"],
                "text_observation": result["text_observation"],
                # "image_list": result["image_list"],
                "chosen": [],
                "rejected": [],
                "source_name": result["source_name"],
            }
        
        response = result["response"] if "response" in result else []
        type_data = {
            "thought": result["thought"],
            "action": result["action"],
            "response": response,
            "score": get_score(response, split_indicator) if split_indicator != "prob" else get_score(result["judge_probs"], split_indicator),
        }
        if split_indicator == "prob":
            type_data["judge_probs"] = result["judge_probs"]
        if result["type"] == "chosen":
            grouped_task_dict[task_name]["chosen"].append(type_data)
        elif result["type"] == "rejected":
            grouped_task_dict[task_name]["rejected"].append(type_data)
    
    return list(grouped_task_dict.values())


def processing_results(results, evaluation_mode: str, num_generate: int):
    if "judge_probs" in results[0]:
        split_indicator = "prob"
    else:
        if evaluation_mode == "judge_with_checklist_generation" or evaluation_mode == "judge_with_gt_checklist":
            split_indicator = "CHECKLIST EVALUATION" 
        else:
            split_indicator = "SCORE"


    grouped_results = group_by_task(results, split_indicator)

    mind2web_results = []
    webarena_results = []
    mind2web_task_results = []
    mind2web_website_results = []
    mind2web_domain_results = []
    
    for grouped_result in grouped_results:
        if "mind2web" in grouped_result["source_name"]:
            mind2web_results.append(grouped_result)
            if grouped_result["source_name"] == "mind2web_test_task":
                mind2web_task_results.append(grouped_result)
            elif grouped_result["source_name"] == "mind2web_test_website":
                mind2web_website_results.append(grouped_result)
            elif grouped_result["source_name"] == "mind2web_test_domain":
                mind2web_domain_results.append(grouped_result)
        elif "webarena" in grouped_result["source_name"]:
            webarena_results.append(grouped_result)
            
    try:
        final_stats = {
            "mind2web": {
                "MRR": {},
                "Accuracy": {},
                "Traj_Accuracy": {},
            },
            "webarena": {
                "MRR": {},
                "Accuracy": {},
                "Traj_Accuracy": {},
            },
            "mind2web_task": {
                "MRR": {},
                "Accuracy": {},
                "Traj_Accuracy": {},
            },
            "mind2web_website": {
                "MRR": {},
                "Accuracy": {},
                "Traj_Accuracy": {},
            },
            "mind2web_domain": {
                "MRR": {},
                "Accuracy": {},
                "Traj_Accuracy": {},
            },
        }
        for source_results in [
            ("mind2web", mind2web_results), 
            ("webarena", webarena_results),
            ("mind2web_task", mind2web_task_results),
            ("mind2web_website", mind2web_website_results),
            ("mind2web_domain", mind2web_domain_results)
        ]:
            average_stats = calculate_stats(source_results[1], "average")
            # self_consistency_stats = calculate_stats(source_results[1], "self_consistency")
            for metric in average_stats:
                final_stats[source_results[0]][metric]["Average"] = average_stats[metric]
            # for metric in self_consistency_stats:
            #     final_stats[source_results[0]][metric]["Self_Consistency"] = self_consistency_stats[metric]
        
        if num_generate == 1:
            for source_name in final_stats:
                for metric in final_stats[source_name]:
                    print(f"{round(100 * final_stats[source_name][metric]['Average'], 2)}", end=", ")
            print()
        else:
            for agg_func in ["Average"]:
                print(f"{agg_func}")
                for source_name in final_stats:
                    for metric in final_stats[source_name]:
                        print(f"{round(100 * final_stats[source_name][metric][agg_func], 2)}", end=", ")
                print()
    except Exception as e:
        print(e)
        return grouped_results, None    
    

    return grouped_results, final_stats