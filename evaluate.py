import time
import json
import pulp
from lp_engine import solve_with_pulp as run_pulp
from fast_assign import build_greedy_schedule as greedy_scheduler


def evaluate_instance(idx: int):
    with open(f"instance_{idx}.json", "r", encoding="utf-8") as f:
        instance_data = json.load(f)

    print("Greedy test...")
    t0 = time.time()
    greedy_cost, _ = greedy_scheduler(
        instance_data["employees"], instance_data["shifts"], instance_data["days"]
    )
    greedy_elapsed_s = time.time() - t0
    greedy_elapsed_ms = greedy_elapsed_s * 1000.0

    print("PuLP test...")
    pulp_model, pulp_elapsed_s = run_pulp(idx)
    pulp_elapsed_ms = pulp_elapsed_s * 1000.0
    status_str = pulp.LpStatus[pulp_model.status]

    if status_str == "Optimal":
        pulp_cost = float(pulp.value(pulp_model.objective))
        pulp_cost_str = f"{pulp_cost:.2f}"
    elif status_str in ("Infeasible", "Unbounded"):
        pulp_cost = float("inf")
        pulp_cost_str = "Neizvodljivo"
    else:
        val = pulp.value(pulp_model.objective)
        if val is None:
            pulp_cost = float("inf")
            pulp_cost_str = f"Nije optimalno ({status_str})"
        else:
            pulp_cost = float(val)
            pulp_cost_str = f"Najbolje nađeno: {pulp_cost:.2f}"

    greedy_cost_str = (
        f"{greedy_cost:.2f}" if greedy_cost != float("inf") else "Neizvodljivo"
    )

    return {
        "id": idx,
        "rate_range": instance_data["instance_info"]["rate_range"],
        "hours_range": instance_data["instance_info"]["hours_range"],
        "pulp_cost": pulp_cost,
        "pulp_cost_str": pulp_cost_str,
        "pulp_time": f"{pulp_elapsed_ms:.2f} ms / {pulp_elapsed_s:.3f} s",
        "greedy_cost": greedy_cost,
        "greedy_cost_str": greedy_cost_str,
        "greedy_time": f"{greedy_elapsed_ms:.2f} ms / {greedy_elapsed_s:.3f} s",
        "pulp_status": status_str,
    }


if __name__ == "__main__":
    summary = []
    for i in [1, 2, 3]:
        print(f"Evaluacija instance {i}")
        summary.append(evaluate_instance(i))

    print(
        "\n-------------------------------------------------  REZULTATI  -------------------------------------------------"
    )
    print(
        f"{'Instanca':<10} | {'Satnica':<15} | {'Max sati':<15} | "
        f"{'PuLP Trošak':<28} | {'Greedy Trošak':<20} | "
        f"{'PuLP Vrijeme':<25} | {'Greedy Vrijeme':<25}"
    )
    print("-" * 130)

    for r in summary:
        print(
            f"{r['id']:<10} | "
            f"{r['rate_range']:<15} | "
            f"{r['hours_range']:<15} | "
            f"{r['pulp_cost_str']:<28} | "
            f"{r['greedy_cost_str']:<20} | "
            f"{r['pulp_time']:<25} | "
            f"{r['greedy_time']:<25}"
        )
