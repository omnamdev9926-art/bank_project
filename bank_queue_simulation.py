"""
BANK QUEUE MANAGEMENT SIMULATION
Course: Solving Problems Through Modelling and Simulation

QUESTION WE ANSWER:
    How many tellers (counters) should the bank keep open so that customers
    do not wait too long, without wasting money on idle tellers?

HOW IT WORKS (simple words):
    1. Customers arrive at random times.
    2. Each customer needs a random amount of service time.
    3. If a teller is free, the customer is served; otherwise waits in a queue.
    4. We run this "virtual bank" for a full day, many times, and record
       waiting times and how busy the tellers are.
    5. We repeat for 1, 2, 3 ... tellers and compare.

Run:   python bank_queue_simulation.py
Needs: pip install simpy numpy pandas matplotlib
"""

import random
import simpy
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # lets us save graphs without opening a window
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# 1. INPUT PARAMETERS (change these to experiment)
# ----------------------------------------------------------------------
SIM_TIME = 360            # bank open for 360 minutes (10 AM to 4 PM)
ARRIVAL_RATE = 0.5        # on average 0.5 customers/minute = 1 every 2 min
PEAK_START, PEAK_END = 120, 210   # lunch rush: 12 PM to 1:30 PM (minutes from open)
PEAK_MULTIPLIER = 1.6     # arrivals are 1.6x faster during the rush
MAX_PATIENCE = 20         # customer leaves if waiting more than 20 minutes
N_RUNS = 100              # repeat each experiment 100 times for reliable averages
TELLER_OPTIONS = [1, 2, 3, 4, 5, 6]

# Customer types: name -> (probability, average service time in minutes)
CUSTOMER_TYPES = {
    "Cash Deposit/Withdrawal": (0.55, 3),
    "Enquiry / Passbook":      (0.25, 2),
    "Account Opening / Loan":  (0.20, 10),
}


# ----------------------------------------------------------------------
# 2. HELPER FUNCTIONS
# ----------------------------------------------------------------------
def pick_customer_type():
    """Randomly choose a customer type based on the probabilities above."""
    names = list(CUSTOMER_TYPES.keys())
    probs = [CUSTOMER_TYPES[n][0] for n in names]
    return random.choices(names, weights=probs)[0]


def current_arrival_rate(now):
    """Arrival rate is higher during the lunch rush."""
    if PEAK_START <= now < PEAK_END:
        return ARRIVAL_RATE * PEAK_MULTIPLIER
    return ARRIVAL_RATE


# ----------------------------------------------------------------------
# 3. THE SIMULATION MODEL
# ----------------------------------------------------------------------
class Bank:
    def __init__(self, env, num_tellers):
        self.env = env
        self.tellers = simpy.Resource(env, capacity=num_tellers)
        self.records = []          # one row per customer
        self.busy_time = 0.0       # total minutes tellers spent serving
        self.queue_log = []        # (time, queue length) for plotting
        self.num_tellers = num_tellers


def customer(env, cid, bank):
    """Life of ONE customer: arrive -> wait -> get served -> leave."""
    arrival = env.now
    ctype = pick_customer_type()
    mean_service = CUSTOMER_TYPES[ctype][1]

    with bank.tellers.request() as req:
        # Wait for a teller OR give up after MAX_PATIENCE minutes
        result = yield req | env.timeout(MAX_PATIENCE)

        if req in result:
            wait = env.now - arrival
            service = random.expovariate(1.0 / mean_service)
            service_start = env.now
            yield env.timeout(service)
            bank.busy_time += max(0.0, min(env.now, SIM_TIME) - service_start)
            bank.records.append({
                "id": cid, "type": ctype, "arrival": arrival,
                "wait": wait, "service": service, "served": True,
            })
        else:
            # Customer got tired of waiting and left (reneging)
            bank.records.append({
                "id": cid, "type": ctype, "arrival": arrival,
                "wait": MAX_PATIENCE, "service": 0, "served": False,
            })


def customer_generator(env, bank):
    """Creates new customers again and again at random gaps."""
    cid = 0
    while True:
        gap = random.expovariate(current_arrival_rate(env.now))
        if env.now + gap >= SIM_TIME:
            break
        yield env.timeout(gap)
        cid += 1
        env.process(customer(env, cid, bank))


def queue_monitor(env, bank):
    """Every minute, note down how many people are waiting."""
    while env.now < SIM_TIME:
        bank.queue_log.append((env.now, len(bank.tellers.queue)))
        yield env.timeout(min(1, SIM_TIME - env.now))


def run_once(num_tellers, seed):
    """Simulate ONE full day at the bank. Returns summary numbers."""
    random.seed(seed)
    env = simpy.Environment()
    bank = Bank(env, num_tellers)
    env.process(customer_generator(env, bank))
    env.process(queue_monitor(env, bank))
    env.run()

    df = pd.DataFrame(bank.records, columns=[
        "id", "type", "arrival", "wait", "service", "served",
    ])
    served = df[df["served"]]
    utilization = bank.busy_time / (num_tellers * SIM_TIME) * 100 if SIM_TIME else 0

    return {
        "tellers": num_tellers,
        "customers": len(df),
        "served": len(served),
        "left_unserved": int((~df["served"]).sum()),
        "avg_wait": df["wait"].mean() if not df.empty else 0.0,
        "max_wait": df["wait"].max() if not df.empty else 0.0,
        "avg_queue_len": np.mean([q for _, q in bank.queue_log]),
        "utilization_%": min(utilization, 100),
    }, bank


# ----------------------------------------------------------------------
# 4. EXPERIMENTS: try different numbers of tellers
# ----------------------------------------------------------------------
def run_experiments():
    all_rows = []
    for n in TELLER_OPTIONS:
        for run in range(N_RUNS):
            summary, _ = run_once(n, seed=run)
            all_rows.append(summary)
    df = pd.DataFrame(all_rows)
    return df.groupby("tellers").mean().round(2)


# ----------------------------------------------------------------------
# 5. GRAPHS
# ----------------------------------------------------------------------
def make_graphs(results):
    # Graph 1: wait time vs tellers
    plt.figure(figsize=(7, 4.5))
    plt.plot(results.index, results["avg_wait"], marker="o", label="Average wait")
    plt.plot(results.index, results["max_wait"], marker="s", label="Maximum wait")
    plt.axhline(5, color="red", linestyle="--", label="Target: 5 min")
    plt.xlabel("Number of tellers")
    plt.ylabel("Waiting time (minutes)")
    plt.title("Waiting time vs number of tellers")
    plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig("graph1_wait_vs_tellers.png", dpi=150); plt.close()

    # Graph 2: utilization
    plt.figure(figsize=(7, 4.5))
    plt.bar(results.index, results["utilization_%"], color="teal")
    plt.axhline(85, color="red", linestyle="--", label="Too busy above 85%")
    plt.xlabel("Number of tellers")
    plt.ylabel("Teller utilization (%)")
    plt.title("How busy are the tellers?")
    plt.legend(); plt.tight_layout()
    plt.savefig("graph2_utilization.png", dpi=150); plt.close()

    # Graph 3: customers who left without service
    plt.figure(figsize=(7, 4.5))
    plt.bar(results.index, results["left_unserved"], color="indianred")
    plt.xlabel("Number of tellers")
    plt.ylabel("Customers who left without service (per day)")
    plt.title("Lost customers vs number of tellers")
    plt.tight_layout()
    plt.savefig("graph3_lost_customers.png", dpi=150); plt.close()


def queue_over_time_graph():
    """Graph 4: queue length during one day for 2, 3 and 4 tellers."""
    plt.figure(figsize=(9, 4.5))
    for n in [2, 3, 4]:
        _, bank = run_once(n, seed=42)
        t, q = zip(*bank.queue_log)
        plt.plot(t, q, label=f"{n} tellers")
    plt.axvspan(PEAK_START, PEAK_END, color="orange", alpha=0.2, label="Lunch rush")
    plt.xlabel("Minutes since bank opened")
    plt.ylabel("People waiting in queue")
    plt.title("Queue length through the day")
    plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig("graph4_queue_over_time.png", dpi=150); plt.close()


# ----------------------------------------------------------------------
# 6. RECOMMENDATION
# ----------------------------------------------------------------------
def recommend(results):
    """Smallest number of tellers with avg wait <= 5 min and few lost customers."""
    good = results[(results["avg_wait"] <= 5) & (results["left_unserved"] <= 2)]
    if len(good):
        best = good.index[0]
        row = results.loc[best]
        return (f"RECOMMENDATION: Use {best} tellers. Average wait is "
                f"{row['avg_wait']} min, tellers are {row['utilization_%']}% busy, "
                f"and only {row['left_unserved']} customers leave per day.")
    return "No option met the target. Try more tellers or change the parameters."


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------
if __name__ == "__main__":
    print("Running simulation... (about 30-60 seconds)\n")
    results = run_experiments()

    pd.set_option("display.width", 200)
    print(results[["customers", "served", "left_unserved", "avg_wait",
                   "max_wait", "avg_queue_len", "utilization_%"]])
    results.to_csv("results.csv")

    make_graphs(results)
    queue_over_time_graph()

    print("\n" + recommend(results))
    print("\nSaved: results.csv and graph1..graph4 PNG files.")
