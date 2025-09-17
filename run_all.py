from make_data import create_instance
from evaluate import evaluate_instance

def run_for_size(n_employees: int):
    print(f"\n----------------  REZULTATI (Instanca sa {n_employees} zaposlenih)  ----------------")
    for i in [1, 2, 3]:
        create_instance(i, n_employees)
    summary = [evaluate_instance(i) for i in [1, 2, 3]]
    print(f"{'Instanca':<10} | {'Satnica':<15} | {'Max sati':<15} | "
          f"{'PuLP Trošak':<20} | {'Greedy Trošak':<20} | "
          f"{'PuLP Vrijeme':<25} | {'Greedy Vrijeme':<25}")
    print("-" * 120)
    for r in summary:
        pulp_cost_str = f"{r['pulp_cost']:.2f}" if r['pulp_cost'] != float('inf') else r['pulp_cost_str']
        greedy_cost_str = f"{r['greedy_cost']:.2f}" if r['greedy_cost'] != float('inf') else r['greedy_cost_str']
        print(f"{r['id']:<10} | {r['rate_range']:<15} | {r['hours_range']:<15} | "
              f"{pulp_cost_str:<20} | {greedy_cost_str:<20} | "
              f"{r['pulp_time']:<25} | {r['greedy_time']:<25}")

if __name__ == "__main__":
    for N in [10, 50, 500, 1000]:
        run_for_size(N)
