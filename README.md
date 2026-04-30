# User-Centric Explainable Anomaly Detection in Graph-Based Database Systems

A proof-of-concept framework that adds a **post-hoc explanation layer** on top of graph-based anomaly detection (GAD) systems, addressing the "black box" problem that makes most GAD outputs unactionable for human analysts. GAD leverages the structural properties of data to
identify aberrations that traditional methodologies forego. However, the majority of these
GAD models are “black boxes”, i.e., they fulfill their objective of anomaly detection,
without offering any justification for their outputs. This lack of transparency is a
significant problem in the adoption of this methodology in domains like finance,
cybersecurity, etc, where accountability and understanding is a critical metric. This paper
identifies this explainability gap and proposes a novel framework to address it. Our
proposed approach functions as an explanation module, that upon receiving a flagged
anomaly from any GAD model, queries the local subgraph of the entity from the database.
It then performs a comparative analysis on the subgraph’s statistical properties against a
baseline of normal entities. The final output is a human readable report explaining why the
entity was deemed anomalous. This thereby enhances the accountability and utility of GAD
systems in real world domains.


---

## Motivation

Graph-based anomaly detection models: IsolationForest, GNNs, GAEs, etc. are effective at flagging anomalies but offer no justification for their outputs. A fraud analyst handed a list of 21 suspicious user IDs has no idea where to begin. This project proposes a lightweight explanation module that sits *on top of* any existing GAD model and produces human-readable reports.

---

## Architecture

![Pipeline Architecture](assets/architecture.png)

The pipeline runs in three phases:

1. **Data Generation** — A synthetic financial transaction database (50,000 transactions, 2,005 users) is created in SQLite, with a planted fraud ring (users 2001–2005) for ground truth validation.
2. **Anomaly Detection — The Spotter** — Graph features (in/out degree, total amounts sent/received) are engineered via NetworkX and fed into scikit-learn's `IsolationForest`.
3. **Explanation Module — The Detective** — For each flagged entity, Z-scores are computed against a normal-entity baseline and formatted into a human-readable console report and a `anomaly_report.csv`.

---

## Results 

Note: Refer to docs/ for in depth analysis.

The model flagged 21 users, successfully capturing all 5 planted fraud ring members. The explanation module then separated these into two categories:

**Category 1 — True Positives:** Users with statistically extreme Z-scores (>3σ), flagged with clear quantitative evidence.



**Category 2 — Ambiguous Positives:** Users flagged by the ML model due to rare feature *combinations*, but with no single extreme metric — allowing analysts to confidently deprioritize these.


---

## Novel Contribution

Unlike tools such as GNNExplainer — which explains a model's internal mathematics to ML researchers — this module explains the **statistical behavior of the entity itself**, in plain language, for analysts.

| | GNNExplainer | This Framework |
|---|---|---|
| **Explains** | How the model's math led to a decision | The statistical behaviour of the flagged user |
| **Target user** | ML researchers | Fraud analysts |
| **Output** | Subgraph with feature importance scores | Human-readable report + CSV |

Crucially, the explanation module is **model-agnostic**: swap out `IsolationForest` for a GNN or GAE and the explainer requires no changes.

---

## Stack

- Python
- SQLite
- pandas
- NetworkX
- scikit-learn

---

## Limitations & Future Work

- Currently uses four hand-engineered graph features; richer topological metrics (betweenness centrality, clustering coefficient) could improve signal
- The explanation module does not yet query a true subgraph neighborhood from the DBMS — a natural next step toward the full proposed architecture
- Evaluation is on synthetic data; real-world financial datasets would stress-test robustness

---

## Reference

Rajasekaran, A. (2025). *User Centric Explainable Anomaly Detection in Graph-Based Database Systems.*
