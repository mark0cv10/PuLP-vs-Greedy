from math import inf
from typing import Dict, List, Tuple, Any

def build_greedy_schedule(
    staff: Dict[str, Dict[str, Any]],
    shift_defs: Dict[str, Dict[str, int]],
    weekday_list: List[str]
) -> Tuple[float, Dict[str, List[Tuple[str, str]]]]:

    assignment: Dict[str, List[Tuple[str, str]]] = {emp: [] for emp in staff}
    remaining: Dict[str, int] = {emp: staff[emp]["max_hours"] for emp in staff}
    total_cost: float = 0.0

    avg_rate = sum(p["rate"] for p in staff.values()) / max(1, len(staff))
    sorted_shifts = sorted(
        shift_defs.items(),
        key=lambda kv: (-kv[1]["required"], -(kv[1]["duration"] * avg_rate))
    )

    for day in weekday_list:
        worked_today = {emp: False for emp in staff}

        for shift_name, shift_info in sorted_shifts:
            need = shift_info["required"]
            dur = shift_info["duration"]

            candidates = [
                emp for emp, props in staff.items()
                if (shift_name in props["availability"][day]
                    and remaining[emp] >= dur
                    and not worked_today[emp])
            ]

            candidates.sort(key=lambda e: (staff[e]["rate"], -remaining[e]))

            taken = 0
            for emp in candidates:
                if taken >= need:
                    break
                assignment[emp].append((day, shift_name))
                remaining[emp] -= dur
                total_cost += staff[emp]["rate"] * dur
                worked_today[emp] = True
                taken += 1

            if taken < need:
                return inf, None

    return total_cost, assignment
