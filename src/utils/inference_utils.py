import time

from multiprocessing import Process, Manager
from tqdm import tqdm


def worker_main(work_queue, result_queue, process_func, config):
    while True:
        item = work_queue.get()
        if item is None:
            result_queue.put(None)
            break
        try:
            results, cost = process_func(config, item)
            result_queue.put((results, cost))
        except Exception as e:
            item_info = item.get('idx', item.get('id', 'unknown item'))
            print(f"Error processing item {item_info}: {e}")
            result_queue.put(None)
        finally:
            work_queue.task_done()

def run_parallel_evaluation(dataset, process_func, config, num_workers, description):
    """
    Runs parallel evaluation on the given dataset and returns the results.

    Args:
        dataset (list or datasets.Dataset): Data to evaluate.
        process_func (callable): Function to process each data item.
        config (dict): Configuration for the process_func.
        num_workers (int): Number of worker processes to use.
        description (str): Description to display on the tqdm progress bar.

    Returns:
        tuple: (list of evaluation results, total cost)
    """
    manager = Manager()
    work_queue = manager.Queue()
    result_queue = manager.Queue()

    # Add data to the work queue
    dataset_list = list(dataset) if not isinstance(dataset, list) else dataset
    for data in dataset_list:
        work_queue.put(data)
    
    # Add termination signals for workers
    for _ in range(num_workers):
        work_queue.put(None)

    # Start parallel processing
    processes = []
    for _ in range(num_workers):
        p = Process(target=worker_main, args=(work_queue, result_queue, process_func, config))
        p.start()
        processes.append(p)
    
    # Show progress bar and collect results
    process_results = []
    process_cost = 0
    completed_workers = 0

    with tqdm(total=len(dataset_list), desc=description) as pbar:
        while completed_workers < num_workers:
            result_item = result_queue.get()
            if result_item is None:
                completed_workers += 1
            else:
                results, cost = result_item
                if results is not None:
                    process_results.append(results)
                    process_cost += cost if cost is not None else 0
                pbar.update(1)

    # Wait for all processes to finish
    for p in processes:
        p.join()

    # Collect remaining results
    while not result_queue.empty():
        result_item = result_queue.get_nowait()
        if result_item is not None:
            results, cost = result_item
            if results is not None:
                process_results.append(results)
                process_cost += cost if cost is not None else 0

    return process_results, process_cost