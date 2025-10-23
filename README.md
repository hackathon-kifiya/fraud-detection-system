# Fraud Detection MVP

A fraud detection system for embedded finance.

## Architecture

```
+--------------------+
                     
        ┌───────────────────────────────────────┐
        │               Fronend                 │
        └───────────────┬───────────────────────┘
                        │
                        │
                        ↓
        ┌───────────────────────────────────────┐
        │           BACKEND                     │
        │  - Orchestration (Workflows)          │
        │  - User Management (Auth)             │
        │  - Input/Ingestion                    │
        │  - Input Sanitization                 │
        └───────────────┬───────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ↓               ↓               ↓
┌───────────────┐ ┌───────────┐ ┌──────────────┐
│ RULE ENGINE   │ │ ML MODEL  │ │   ANOMALY    │
│               │ │           │ │  DETECTION   │
│ Deterministic │ │ XGBoost/NN│ │              │
│ - Blacklist   │ │ - Features│ │ Unsupervised │
│ - Velocity    │ │ - Scoring │ │ - Isolation  │
│ - Geo checks  │ │           │ │ - Autoencoder│
│               │ │           │ │              │
│ ~50ms         │ │ ~200ms    │ │ ~150ms       │
└───────┬───────┘ └─────┬─────┘ └──────┬───────┘
        │               │               │
        └───────────────┼───────────────┘
                        ↓
        ┌───────────────────────────────────────┐
        │   RISK AGGREGATION ENGINE             │
        │                                       │
        │   Score = 0.3×Rule + 0.5×ML + 0.2×AD  │
        │                                       │
        │   Thresholds:                         │
        │   < 0.3  → Auto-Approve               │
        │   0.3-0.7 → Human Review              │
        │   > 0.7  → Auto-Block                 │
        └───────────────┬───────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ↓               ↓               ↓
    ┌────────┐  ┌──────────────┐  ┌────────┐
    │APPROVE │  │ HUMAN REVIEW │  │ BLOCK  │
    └────────┘  └──────┬───────┘  └────────┘
                       │
                       │
                       ↓
        ┌──────────────────────────────────────┐
        │   FEEDBACK LOOP                      │
        │   Labels → Model Retraining          │
        └──────────────────────────────────────┘
                   
```


## Use cases

https://docs.google.com/spreadsheets/d/1YFAoreEE3M_yJxrjLkx92qoIPFh0YinAQshdZ5iMICQ/edit?usp=sharing