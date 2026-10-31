# Capstone Report: Refresh / Content Opportunity Scoring

- **Author:** Hassan Ali Akhund
- **Lane:** Lane 2, Refresh / Content Opportunity Scoring
- **Repo:** https://github.com/hassanali241/FlyRank
- **Paper:** https://hassanali241.github.io/FlyRank/
- **Date:** October 2026

The full argument lives in the paper and in [`notebooks/capstone.ipynb`](notebooks/capstone.ipynb). This file maps it onto the eight rubric axes.

## 1. Problem framing

The decision is which pages a content reviewer opens first in a month. The unit is one page at one monthly decision date. The output is a ranked review queue with a suggested action and reason codes per page. A false positive wastes review time; a false negative costs the clicks a page keeps losing, and that cost grows with its demand. ML helps because no single signal separates decliners well (the best alone reaches an AUC near 0.6), and signals interact in ways a hand rule can't hold.

## 2. Data safety

The data is the pseudonymized warehouse release `v20260703`: daily fact partitions February to June 2026, plus `dim_content` creation dates. I excluded the July-snapshot fields (update dates, word count, deleted flag), because about 81% of pages show an update after the decision date. GA4 and AI-session columns are too sparse to use. Ids are used only for grouping and splitting, and no product flags exist. Nothing client-identifying appears in `work/` or `docs/`; page ids in the paper are truncated pseudonyms.

## 3. Baseline

The rule is frozen in week 4. It flags pages whose late-month momentum is below -0.1 and whose CTR is below their position tier's median, then ranks them by slide size. Both signals passed a bucket check first; volume failed it (OPPOSITE). The rule is scored on exactly the same pages as the model in every design. On sealed June it reaches ROC AUC 0.602 and 0.82 precision at 50 once the one dominant client is excluded.

## 4. Model / analysis

A random forest (300 trees, min leaf 50, seed 42) uses seven features: log impressions, days visible, weighted position, late-month momentum, content age, CTR, and the CTR gap to the tier median (fitted on training rows). The target is declined next month: per-day impressions more than 20% down and at least 20 points worse than the client's median page. Logistic regression and gradient boosting were compared and not chosen. A client-level momentum feature was dropped after the week 6 audit.

## 5. Evaluation

The designs are a random 80/20 split (as the "before"), GroupKFold by client, time-forward to May, and a sealed June month scored once. The forest's ROC AUC was 0.707, 0.729 and 0.703 against the rule's 0.595, 0.634 and 0.602, with average precision about 0.10 higher throughout. At K = 50 to 500 the two are within a few points. Errors fall into two groups. Late-month dips that recovered, or that fell with their whole site, rank high but didn't decline. Large, steady pages that collapsed with no warning are the costliest misses.

## 6. Interpretation

Late-month momentum carries the model; shuffling it costs about 0.19 average precision on June. CTR below the tier norm adds a little; position and age add nothing measurable on June. The negative results were useful too. Bigger pages decline less often, the random split overstates skill by about 0.04 to 0.06 AUC, and the rule's perfect June top 500 is one client's churn.

## 7. Recommendation

The July queue (96,727 pages, 43 clients) is ordered by demand at risk and capped at 10 pages per client in the top 50. Work it in this order: indexing checks for pages that dropped out; refresh plus snippet rewrite for sliding, under-clicked pages; content refresh for sliding pages; snippet rewrites for under-clicked page-one pages; a site check when a client hits the cap. Log every action. The confidence is decision-support, not causal.

## 8. Reproducibility

```bash
git clone https://github.com/hassanali241/FlyRank && cd FlyRank
pip install -r assignment-06/requirements.txt jupyter
# accept the dataset terms on Hugging Face, then set HF_TOKEN (read token) in the environment
jupyter nbconvert --to notebook --execute --inplace work/notebooks/capstone.ipynb
```

The seed is 42 everywhere. Pinned versions: pandas 3.1.0, numpy 2.5.4, duckdb 2.0.0, scikit-learn 1.9.1, scipy 1.18.1, huggingface_hub 2.4.0. Re-running regenerates `docs/paper/results.json` and `results.js`, which the paper reads.

---

> Claims checklist: observed / measured / directional / decision-support language throughout · base rate printed next to every metric · no causal or algorithm claims.
