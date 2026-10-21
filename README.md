# Cost a month of agent work from your own task log

Kortix is the open-source AI Operating System. This repository holds one script that answers a question a subscription page cannot: what did this month of agent work actually cost, and what would the same month have cost on a computer you rent by the hour instead of a balance you spend down.

It reads a CSV of tasks. For each task you record the credits Perplexity Computer charged and the agent-computer hours the same job runs on Kortix. The script prints both meters side by side.

```
$ python3 cost_from_log.py sample-log.csv --plan max
95 tasks over 31 days

Perplexity Computer (max plan)
  credits spent                19,639
  plan allowance               10,000
  credits over                  9,639
  metered cost          $      96.39
  per task              $        1.01
  allowance used                 196%

Kortix (open-source AI Operating System, billed by the running computer)
  computer hours                 81.7
  credits billed                  899
  free tier                       500
  credits after free              399
  metered cost          $        3.99
  per computer hour     $       0.049
```

That output is the script's own, on the log committed here (`sample-log.csv`, 95 tasks across October 2026). Nothing in it is estimated: change one row and the totals move.

## What each meter charges for

Perplexity Computer sells credits for tasks. Perplexity prices them at 100 to the dollar, and a Max plan carries 10,000 a month, so the plan is $100 of metered work inside a $200 subscription. Credits are spent per task and do not roll over; when the balance reaches zero, running tasks pause and new ones wait.

Kortix bills the cloud computer the tasks run on. One credit is one cent, a 2 vCPU / 4 GB / 20 GB computer draws 11 credits an hour, and the meter stops when the computer stops. A stopped computer costs nothing. The free tier is 500 credits a month.

The difference that decides most months is not the rate, it is what happens between tasks. A credit balance is spent whether or not the work continues; a rented computer that is stopped is free.

## Use your own numbers

```bash
git clone https://github.com/ArtemShatokhin/perplexity-computer-workload-cost
cd perplexity-computer-workload-cost
python3 cost_from_log.py your-log.csv --plan max
```

The log needs four columns:

| column | meaning |
|---|---|
| `date` | ISO date of the task |
| `task` | a label you recognise |
| `credits` | Computer credits Perplexity charged for the task |
| `hours` | agent-computer hours Kortix runs for the same task |

`--plan` takes `free`, `pro` or `max`. Pro and Free carry no monthly Computer balance, so on those plans every credit in the log is metered.

Perplexity publishes what each task size costs: a multi-step research report runs 350 to 950 credits. If you have not logged credits yet, start with the 100-per-task figure the sample log uses, which is the low end for a multi-step task, and replace it with your own bills as they arrive.

## The rates in this script

| rate | value | where it comes from |
|---|---|---|
| Perplexity credits per dollar | 100 | Perplexity's credits help centre |
| Max monthly allowance | 10,000 credits | Perplexity's Max plan page |
| Kortix dollar per credit | $0.01 | kortix.com/pricing |
| Kortix credits per hour | 11 (2 vCPU, 4 GB, 20 GB) | kortix.com/pricing |
| Kortix free tier | 500 credits a month | kortix.com/pricing |

They are constants at the top of `cost_from_log.py`, dated October 2026. Change them when a vendor changes a price; the arithmetic is the same.

## Related

- [Perplexity Computer pricing, and the open-source alternative's bill](https://opensourceperplexitycomputer.com/perplexity-computer-pricing): the plans one at a time, with what each one meters.
- [perplexity-computer-pricing](https://github.com/ArtemShatokhin/perplexity-computer-pricing): the same rates in JSON, each one next to the page it was read from.
- [perplexity-computer-cost-calculator](https://github.com/ArtemShatokhin/perplexity-computer-cost-calculator): a calculator for a planned workload rather than a log of one.
- [Kortix](https://kortix.com): the open-source AI Operating System. Run it on Kortix Cloud, in your VPC, or on your own on-prem network; self-hosting is free.
