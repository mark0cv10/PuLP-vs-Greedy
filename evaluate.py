import time
import json
import pulp
from lp_engine import solve_with_pulp as run_pulp
from fast_assign import build_greedy_schedule as greedy_scheduler


def evaluate_instance(idx):
    with open(f"instance_{idx}.json") as f:
        instance_data = json.load(f)

    print("Greedy test...")
    t0 = time.time()
    greedy_cost, _ = greedy_scheduler(instance_data["employees"], instance_data["shifts"], instance_data["days"])
    greedy_elapsed_s = time.time() - t0
    greedy_elapsed_ms = greedy_elapsed_s * 1000

    print("PuLP test...")
    pulp_model, pulp_elapsed_s = run_pulp(idx)
    pulp_elapsed_ms = pulp_elapsed_s * 1000
    pulp_cost = pulp.value(pulp_model.objective) if pulp_model.status == 1 else float("inf")

    return {
        "id": idx,
        "rate_range": instance_data["instance_info"]["rate_range"],
        "hours_range": instance_data["instance_info"]["hours_range"],
        "pulp_cost": pulp_cost,
        "pulp_time": f"{pulp_elapsed_ms:.2f} ms / {pulp_elapsed_s:.3f} s",
        "greedy_cost": greedy_cost,
        "greedy_time": f"{greedy_elapsed_ms:.2f} ms / {greedy_elapsed_s:.3f} s"
    }

if __name__ == "__main__":
    summary = []
    for i in [1, 2, 3]:
        print(f"Evaluacija instance {i}")
        summary.append(evaluate_instance(i))

    print("\n-----------------------------------------------  REZULTATI  -----------------------------------------------")
    print(f"{'Instanca':<10} | {'Satnica':<15} | {'Max sati':<15} | "
          f"{'PuLP Trošak':<20} | {'Greedy Trošak':<20} | "
          f"{'PuLP Vrijeme':<25} | {'Greedy Vrijeme':<25}")
    print("-" * 130)

    for res in summary:
        pulp_cost_str = f"{res['pulp_cost']:.2f}" if res['pulp_cost'] != float("inf") else "Neizvodljivo"
        greedy_cost_str = f"{res['greedy_cost']:.2f}" if res['greedy_cost'] != float("inf") else "Neizvodljivo"

        print(
            f"{res['id']:<10} | "
            f"{res['rate_range']:<15} | "
            f"{res['hours_range']:<15} | "
            f"{pulp_cost_str:<20} | "
            f"{greedy_cost_str:<20} | "
            f"{res['pulp_time']:<25} | "
            f"{res['greedy_time']:<25}"
        )
