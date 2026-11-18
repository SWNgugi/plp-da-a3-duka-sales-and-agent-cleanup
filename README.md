\# Duka Electronics Sales and Agent Network Cleanup



\*\*Name:\*\* Stanley Wanyoike Ngugi | \*\*Cohort:\*\* 1 Mill Devs Cohort 2026



\## Summary

\*\*Engagement 1, Duka Electronics:\*\* exploration of 1,000 orders (January to June 2026) with pandas and a spreadsheet cross-check, answering the Head of Sales' questions on branches, products, weekends and months.

\*\*Engagement 2, Mobile money agents:\*\* audit and cleaning of an unreliable transaction extract, merged with the agent register, with a reusable cleaning pipeline and a Data Quality Report.



\## Regenerate the data

Raw CSVs are not committed. Run `python generate\_data.py` to create `duka\_sales.csv`, `agents.csv` and `agent\_transactions.csv`.



\## How to run

\- Duka: \[Open in Colab](https://colab.research.google.com/github/SWNgugi/plp-da-a3-duka-sales-and-agent-cleanup/blob/main/duka\_sales\_exploration.ipynb)

\- Agents: \[Open in Colab](https://colab.research.google.com/github/SWNgugi/plp-da-a3-duka-sales-and-agent-cleanup/blob/main/agent\_cleanup.ipynb)



Each notebook clones this repo and regenerates its data in the first cell, so you can use Runtime -> Run all.



\## Duka Executive Summary

\- Duka Electronics earned KES 71.8M from 1,000 orders between 1 January and 29 June 2026, an average of KES 71,793 per order.

\- Nairobi is the strongest branch with KES 26.1M (36.4% of revenue) from 376 orders, and branches rank identically by revenue and by orders because average order values only range from KES 68,353 to KES 75,591.

\- Laptops generate KES 41.5M (57.9% of revenue) from 639 units, while tablets sell the most units (691) but earn only KES 19.3M.

\- Weekends account for 27.7% of orders (277) and 27.8% of revenue, and average order revenue is almost identical (KES 71,972 on weekends versus KES 71,724 on weekdays), so there is no weekend premium.

\- April was the best month (KES 13.5M) and June the worst (KES 10.9M), a 24.0% gap, while the 83 Premium online orders in Nairobi and Mombasa brought in KES 10.2M (14.2% of revenue).



\## Agent data before and after cleaning

Rows: 612 raw -> 600 clean (12 duplicate transactions removed). 20 amounts imputed, 7 transactions with unknown agent AG099 kept as county "Unknown", and 40 amounts flagged as outliers.

