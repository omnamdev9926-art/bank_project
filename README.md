# Bank Queue Management Simulation

## 1. What is this project? (simple words)
A real bank cannot be used for experiments. So we build a **virtual bank in Python**. Customers arrive at random times, need random amounts of time, and wait if all tellers are busy. We run this virtual day 100 times for 1, 2, 3 ... 6 tellers and see which setup works best.

**Question answered:** How many tellers does the bank need so customers don't wait too long, without wasting money on idle tellers?

## 2. How to run it
1. Install Python 3.9 or newer.
2. In a terminal: `pip install simpy numpy pandas matplotlib`
3. Put all files in one folder and run: `python bank_queue_simulation.py`
4. Wait about a minute. It prints a table and saves 4 graphs plus `results.csv`.

## 3. Assumptions (write these in your report)
| Item | Value |
|---|---|
| Bank open | 360 minutes (10 AM to 4 PM) |
| Average arrivals | 1 customer every 2 minutes |
| Lunch rush | 12:00 to 1:30, arrivals 1.6x faster |
| Customer types | Cash 55% (3 min), Enquiry 25% (2 min), Account/Loan 20% (10 min) |
| Queue type | One single line shared by all tellers |
| Patience | Customer leaves after waiting 20 minutes |
| Closing behavior | No new arrivals after closing; customers already in the bank are served or leave after reaching their patience limit |
| Repetitions | 100 runs per teller count (different random seeds) |

Wait and lost-customer results include every customer who arrived during opening hours. Queue length and teller utilization are measured only during opening hours; service for customers already in the bank continues after closing.

## 4. Key concepts
- **Exponential distribution:** used for gaps between arrivals and for service times. It matches real life: many short gaps and a few long ones.
- **Poisson arrivals:** the name for random arrivals whose gaps are exponential.
- **Resource (SimPy):** the tellers. Only a fixed number can serve at once.
- **Utilization:** the share of opening time tellers are busy. Too low means wasted money; too high means long queues.
- **Reneging:** a customer who gets tired of waiting and leaves.
- **Replications:** running the same experiment many times, because one run can be lucky or unlucky.

## 5. Results (average of 100 simulated days)
| Tellers | Avg wait (min) | Max wait (min) | Utilization | Customers lost/day |
|---|---|---|---|---|
| 1 | 17.87 | 20.0 | 98.78% | 115.86 |
| 2 | 12.00 | 20.0 | 92.70% | 41.01 |
| 3 | 5.21 | 18.25 | 76.19% | 7.99 |
| **4** | **1.46** | **10.96** | **58.98%** | **0.66** |
| 5 | 0.41 | 5.87 | 46.59% | 0.01 |
| 6 | 0.16 | 3.09 | 39.02% | 0.03 |

**Conclusion:** 1 or 2 tellers is clearly too few (huge queues, many customers walk away). 3 is borderline. **4 tellers is the best balance:** short waits, almost nobody leaves, and tellers are busy 58% of the time. 5 and 6 only add idle tellers.

(Your numbers may differ slightly if you change the parameters. That is normal in simulation.)

## 6. Report outline
1. Problem statement
2. Objectives
3. Assumptions and input parameters (section 3 table)
4. Model description (arrival, queue, service, departure; draw a flowchart)
5. Python implementation (explain the code sections)
6. Results with graphs 1 to 4
7. Analysis and conclusion (section 5)
8. Limitations and future scope

**Limitations to mention:** single queue only; tellers all have the same speed; no breaks; arrival and service patterns are assumed, not taken from a real bank.
**Future scope:** compare single queue vs. separate queues, priority lane for senior citizens, cost analysis of teller salaries vs. lost customers.

## 7. Likely viva questions and answers
**Q: Why simulation instead of mathematics or real experiment?**
A real bank can't be used for trial and error, and the math (queueing theory) becomes hard when we add rush hours, customer types and walk-aways. Simulation handles all of that easily.

**Q: Why exponential distribution?**
It is the standard model for random arrivals and service times, with many short gaps and a few long ones.

**Q: Why run 100 times?**
One run depends on luck. Averaging many runs gives reliable results.

**Q: What is a discrete-event simulation?**
The system changes only at specific events (customer arrives, service starts, service ends), so the simulation jumps from event to event instead of ticking every second. SimPy works this way.

**Q: What is SimPy?**
A Python library for discrete-event simulation. It provides the clock (`Environment`) and the tellers (`Resource`).

**Q: How did you choose the best number of tellers?**
The smallest number that kept the average wait under 5 minutes and almost no customers leaving.

**Q: How could the model be improved?**
Use real bank data for arrival and service times, add teller breaks, compare queue designs.

## 8. Things you can easily change in the code
At the top of `bank_queue_simulation.py`: `ARRIVAL_RATE` (busier bank), `CUSTOMER_TYPES` (service times), `MAX_PATIENCE`, `TELLER_OPTIONS`.
