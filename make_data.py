import random
import json
import math

REQ_MIN, REQ_MAX = 0.06, 0.18


def create_instance(idx: int, n_employees: int) -> None:

    random.seed(42 + idx)

    weekdays = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    workers = {}
    shift_plan = {}

    low_rate, high_rate = float("inf"), -float("inf")
    low_hours, high_hours = float("inf"), -float("inf")

    for w in range(1, n_employees + 1):
        rate = random.randint(10, 35)
        max_h = random.randint(8, 25)
        workers[f"Worker_{w}"] = {
            "rate": rate,
            "max_hours": max_h,
            "availability": {
                d: (["morning", "afternoon", "evening"]
                    if random.random() > 0.3 else ["morning", "afternoon"])
                for d in weekdays
            },
        }
        low_rate, high_rate = min(low_rate, rate), max(high_rate, rate)
        low_hours, high_hours = min(low_hours, max_h), max(high_hours, max_h)

    def required_workers(shift_type: str) -> int:
        min_available = min(
            sum(1 for emp in workers.values() if shift_type in emp["availability"][d])
            for d in weekdays
        )
        return max(1, int(min_available * random.uniform(REQ_MIN, REQ_MAX)))

    shift_plan["morning"]   = {"duration": 4, "required": required_workers("morning")}
    shift_plan["afternoon"] = {"duration": 6, "required": required_workers("afternoon")}
    shift_plan["evening"]   = {"duration": 4, "required": required_workers("evening")}

    daily_required = sum(shift_plan[s]["required"] for s in shift_plan)
    if daily_required > len(workers):
        factor = (len(workers) / daily_required) * 0.9
        for s in shift_plan:
            shift_plan[s]["required"] = max(1, math.floor(shift_plan[s]["required"] * factor))

    weekly_demand_hours = 7 * sum(
        shift_plan[s]["required"] * shift_plan[s]["duration"] for s in shift_plan
    )
    weekly_capacity_hours = sum(w["max_hours"] for w in workers.values())
    if weekly_demand_hours > weekly_capacity_hours:
        factor = (weekly_capacity_hours / weekly_demand_hours) * 0.9
        for s in shift_plan:
            shift_plan[s]["required"] = max(1, math.floor(shift_plan[s]["required"] * factor))

    for s in shift_plan:
        for d in weekdays:
            while True:
                available = [e for e in workers if s in workers[e]["availability"][d]]
                if len(available) >= shift_plan[s]["required"]:
                    break
                chosen = random.choice(list(workers.keys()))
                if s not in workers[chosen]["availability"][d]:
                    workers[chosen]["availability"][d].append(s)

    with open(f"instance_{idx}.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "employees": workers,
                "shifts": shift_plan,
                "days": weekdays,
                "instance_info": {
                    "rate_range": f"{low_rate}-{high_rate}",
                    "hours_range": f"{low_hours}-{high_hours}",
                },
            },
            f,
            indent=2,
        )


if __name__ == "__main__":
    for k in range(1, 3 + 1):
        create_instance(k, n_employees=1000)
        print(f"Instanca {k} je uspješno generisana.")
