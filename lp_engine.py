import time
import json
import pulp
from itertools import product

def solve_with_pulp(instance_id: int):
    t0 = time.time()

    with open(f"instance_{instance_id}.json", "r") as f:
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

    assign = pulp.LpVariable.dicts(
        "assign", feasible, lowBound=0, upBound=1, cat="Binary"
    )

    deficit = pulp.LpVariable.dicts(
        "deficit", [(d, s) for d in weekdays for s in shift_def], lowBound=0, cat="Integer"
    )

    penalty_per_worker = 10000

    model += (
        pulp.lpSum(
            assign[e, d, s] * staff[e]["rate"] * shift_def[s]["duration"]
            for (e, d, s) in feasible
        )
        + penalty_per_worker * pulp.lpSum(deficit[d, s] for d in weekdays for s in shift_def)
    )

    for d in weekdays:
        for s in shift_def:
            model += (
                pulp.lpSum(assign[e, d, s] for e in staff if (e, d, s) in assign)
                + deficit[d, s]
                == shift_def[s]["required"]
            )

    for e in staff:
        for d in weekdays:
            model += pulp.lpSum(assign[e, d, s] for s in shift_def if (e, d, s) in assign) <= 1

    for e in staff:
        model += pulp.lpSum(
            assign[e, d, s] * shift_def[s]["duration"]
            for d in weekdays for s in shift_def if (e, d, s) in assign
        ) <= staff[e]["max_hours"]

    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=60)
    model.solve(solver)

    elapsed = time.time() - t0
    return model, elapsed
