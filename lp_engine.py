import time
import json
import pulp
from itertools import product


def solve_with_pulp(instance_id: int):

    t0 = time.time()

    with open(f"instance_{instance_id}.json", "r", encoding="utf-8") as f:
        payload = json.load(f)

    staff = payload["employees"]
    shift_def = payload["shifts"]
    weekdays = payload["days"]

    model = pulp.LpProblem("Workforce_Scheduling", pulp.LpMinimize)

    feasible = [
        (e, d, s)
        for e, d, s in product(staff.keys(), weekdays, shift_def.keys())
        if s in staff[e]["availability"][d]
    ]
    assign = pulp.LpVariable.dicts("assign", feasible, 0, 1, cat="Binary")

    model += pulp.lpSum(
        assign[e, d, s] * staff[e]["rate"] * shift_def[s]["duration"]
        for (e, d, s) in feasible
    )

    for d in weekdays:
        for s in shift_def:
            model += (
                pulp.lpSum(assign[e, d, s] for e in staff if (e, d, s) in assign)
                == shift_def[s]["required"]
            )

    for e in staff:
        for d in weekdays:
            model += pulp.lpSum(
                assign[e, d, s] for s in shift_def if (e, d, s) in assign
            ) <= 1

    for e in staff:
        model += pulp.lpSum(
            assign[e, d, s] * shift_def[s]["duration"]
            for d in weekdays for s in shift_def if (e, d, s) in assign
        ) <= staff[e]["max_hours"]

    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=120, options=["ratioGap=0.0"])
    model.solve(solver)

    return model, time.time() - t0
