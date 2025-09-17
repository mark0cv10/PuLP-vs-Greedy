from math import inf
from typing import Dict, List, Tuple, Any, DefaultDict
from collections import defaultdict


def build_greedy_schedule(
    staff: Dict[str, Dict[str, Any]],
    shift_defs: Dict[str, Dict[str, int]],
    weekday_list: List[str],
) -> Tuple[float, Dict[str, List[Tuple[str, str]]]]:


    assignment: Dict[str, List[Tuple[str, str]]] = {e: [] for e in staff}
    remaining: Dict[str, int] = {e: staff[e]["max_hours"] for e in staff}
    total_cost = 0.0

    base_candidates: DefaultDict[str, DefaultDict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
    for d in weekday_list:
        for s in shift_defs:
            cand = [e for e, p in staff.items() if s in p["availability"][d]]
            cand.sort(key=lambda e: (staff[e]["rate"], -staff[e]["max_hours"]))
            base_candidates[d][s] = cand

    def current_candidates(day: str, shift_name: str, worked_today) -> List[str]:
        dur = shift_defs[shift_name]["duration"]
        return [e for e in base_candidates[day][shift_name] if (not worked_today[e] and remaining[e] >= dur)]

    def try_local_swap(day: str, shift_name: str, worked_today) -> Tuple[bool, float]:
        dur = shift_defs[shift_name]["duration"]

        for e in base_candidates[day][shift_name]:
            if worked_today[e]:
                if remaining[e] < dur:
                    continue
                s2 = None
                for (d2, ss2) in assignment[e]:
                    if d2 == day:
                        s2 = ss2
                        break
                if s2 is None:
                    continue

                dur2 = shift_defs[s2]["duration"]

                repl_list = current_candidates(day, s2, worked_today)
                repl_list = [r for r in repl_list if r != e]
                if not repl_list:
                    continue

                repl_list.sort(key=lambda r: (staff[r]["rate"], -remaining[r]))
                r = repl_list[0]

                assignment[e].remove((day, s2))
                remaining[e] += dur2

                assignment[e].append((day, shift_name))
                remaining[e] -= dur

                assignment[r].append((day, s2))
                remaining[r] -= dur2
                worked_today[r] = True

                extra_cost = staff[e]["rate"] * dur + staff[r]["rate"] * dur2 - staff[e]["rate"] * dur2
                return True, extra_cost

        return False, 0.0

    for day in weekday_list:
        worked_today = {e: False for e in staff}

        need = {s: int(shift_defs[s]["required"]) for s in shift_defs}

        while True:
            if sum(need.values()) == 0:
                break

            mrv_order = sorted(
                need.keys(),
                key=lambda s: (need[s] == 0, len(current_candidates(day, s, worked_today)))
            )

            chosen = None
            for s in mrv_order:
                if need[s] == 0:
                    continue
                cand = current_candidates(day, s, worked_today)
                if cand:
                    chosen = (s, cand)
                    break

            if chosen is None:
                swapped, extra = try_local_swap(day, next(k for k, v in need.items() if v > 0), worked_today)
                if swapped:
                    total_cost += extra
                    for s in need:
                        if need[s] > 0:
                            need[s] -= 1
                            break
                    continue
                return inf, None

            s, cand = chosen
            cand.sort(key=lambda e: (staff[e]["rate"], -remaining[e]))
            emp = cand[0]

            dur = shift_defs[s]["duration"]
            assignment[emp].append((day, s))
            remaining[emp] -= dur
            worked_today[emp] = True
            total_cost += staff[emp]["rate"] * dur
            need[s] -= 1

    return total_cost, assignment
