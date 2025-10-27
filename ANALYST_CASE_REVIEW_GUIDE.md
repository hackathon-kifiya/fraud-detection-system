# Analyst Case Review Guide

## Overview

This guide explains how analysts can review cases assigned to them in the fraud detection system.

## Accessing Your Cases

1. **Login** as an analyst user
   - Email: `analyst@fraud-detection.com`
   - Password: `analyst123`

2. **Navigate to "My Assigned Cases"** from the main menu

## Case Detail View

When you click "View" on any case, you'll see a detailed dialog with **4 tabs**:

### Tab 1: Submitted Data
Displays the original data that was submitted for evaluation. The data is shown in an easy-to-read format with:

- **Key-Value Pairs**: All data fields are displayed in a clean grid layout
- **Readable Field Names**: Field names are formatted for readability (e.g., "first_name" becomes "First Name")
- **Raw JSON View**: Toggle to view the complete JSON structure if needed

**Example Data Types:**
- **Transactions**: Amount, currency, location, merchant, timestamps
- **KYC**: Document type, verification results, identity match confidence
- **Loan Requests**: Loan amount, stated income, verified income, credit score
- **Credit History**: Payment history, score changes, collections
- **Repayments**: Payment amounts, sources, patterns

### Tab 2: Evaluation Results
Shows the analysis results from all fraud detection engines:

**Overall Risk Score**
- Color-coded: 🔴 Critical (80-100), 🟠 High (60-79), 🟡 Medium (40-59), 🟢 Low (0-39)
- Based on weighted combination of all engine scores

**Individual Engine Scores:**

1. **Rule Engine Score** (0-100)
   - Multiple high-severity rules triggered (90+)
   - Several suspicious patterns detected (70-89)
   - Minor anomalies detected (<70)

2. **Anomaly Detection Score** (0-100)
   - Highly unusual behavior patterns (90+)
   - Significant behavioral deviations (70-89)
   - Normal behavioral patterns (<70)

3. **ML Prediction Score** (0-100)
   - High fraud probability detected (90+)
   - Moderate fraud risk (70-89)
   - Low fraud probability (<70)

**Additional Information:**
- Evaluation details from engines
- Reason for flagging
- Timestamps and metadata

### Tab 3: Audit Trail
Shows the complete history of actions taken on this case:
- Status changes
- Reviews by other analysts
- Timestamps
- User actions

### Tab 4: Review & Classify
Review the case and submit your classification:

**Options:**
1. **Confirmed Fraud** (Red button) - The case is legitimate fraud
2. **False Positive** (Green button) - The case was incorrectly flagged

**Steps:**
1. Review the submitted data and evaluation results
2. Select a classification
3. Add review notes explaining your decision
4. Click "Submit Classification"

## Understanding the Scores

### Risk Score Interpretation

- **0-39**: 🟢 Low Risk - Likely false positive, normal activity
- **40-59**: 🟡 Medium Risk - Requires review, some anomalies detected
- **60-79**: 🟠 High Risk - Suspicious activity, likely fraud
- **80-100**: 🔴 Critical Risk - Strong indicators of fraud

### Score Sources

1. **Rule Engine**: Evaluates against business rules (transaction limits, frequency, patterns)
2. **Anomaly Detection**: Compares behavior against historical patterns and statistical models
3. **ML Prediction**: Machine learning model prediction based on labeled training data

## Best Practices

1. **Start with the Submitted Data tab** - Understand what was flagged
2. **Review all evaluation results** - Check each engine's assessment
3. **Consider the reason for flagging** - The system explanation provides context
4. **Check the audit trail** - See if others have already reviewed this
5. **Add detailed notes** - Explain your decision for future reference

## Quick Reference

| Priority | Action Required | Typical Review Time |
|----------|----------------|---------------------|
| Urgent   | Immediate      | < 2 hours           |
| High     | Within 24 hours| 4-8 hours           |
| Medium   | Within 3 days  | 1-2 hours           |
| Low      | Within 1 week  | 30-60 minutes       |

## Seeded Test Data

The system includes 15 seeded cases across different types:

- **5 Transaction cases** - Velocity, geographic, structuring patterns
- **4 Loan cases** - Income mismatch, multiple applications, DTI issues
- **3 KYC cases** - Document forgery, identity theft, PEP matches
- **2 Credit cases** - Score manipulation, payment history
- **2 Repayment cases** - Payment source changes, irregular patterns

Each case has:
- Realistic risk scores (68-96)
- Detailed JSON metadata
- Varying priorities and statuses
- Historical timestamps

## Need Help?

- Check the audit trail for previous reviews
- Review the evaluation details for engine reasoning
- Consult with senior analysts on high-priority cases
- Use the "Show Raw JSON" toggle to see complete data structure

