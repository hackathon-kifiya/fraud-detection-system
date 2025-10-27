# Quick Start Guide - Analyst Case Review

## Current Status

✅ **Database seeded** with 60 case assignments for `analyst@fraud-detection.com`  
✅ **Backend running** on http://localhost:8080  
✅ **Frontend running** on http://localhost:3000  
✅ **Code changes applied** to show detailed case information

## How to Access the System

### 1. Open the Frontend
```
http://localhost:3000
```

### 2. Login as Analyst
- **Email**: `analyst@fraud-detection.com`
- **Password**: `analyst123`

### 3. Navigate to "My Assigned Cases"
You should see 60 cases assigned to you.

### 4. Click "View" on Any Case
This opens the detailed case view with 4 tabs:

#### Tab 1: Submitted Data
- Shows the original data in a readable format
- Click "Show Raw JSON" to see the complete JSON structure
- Data includes: transaction history, loan requests, KYC info, etc.

#### Tab 2: Evaluation Results  
Shows scores from all 3 fraud detection engines:

- **Overall Risk Score** (color-coded: 🔴🟠🟡🟢)
- **Rule Engine Score** - Shows which business rules triggered
- **Anomaly Detection Score** - Behavioral analysis
- **ML Prediction Score** - Machine learning fraud probability
- **Reason for Flagging** - Why the system flagged this
- **Additional Details** - Technical information

#### Tab 3: Audit Trail
- Complete history of actions on this case
- Status changes
- Previous reviews

#### Tab 4: Review & Classify
- Mark as **Confirmed Fraud** or **False Positive**
- Add review notes
- Submit your classification

## Test the Enhanced View

### What You Should See:

1. **Original Data Tab**:
   - Clean grid layout with key-value pairs
   - Example for transactions: amount, currency, location, merchant
   - Example for KYC: document type, verification results, confidence

2. **Evaluation Results Tab**:
   - Large overall risk score at the top (color changes based on value)
   - Three cards showing individual engine scores
   - Each card has:
     - Score value (0-100)
     - Description of what it means
     - Alert showing severity
   - Additional evaluation details at the bottom

## Troubleshooting

### If you don't see cases:
1. Wait 30 seconds for services to fully start
2. Refresh the page
3. Log out and log back in
4. Check browser console for errors

### If cases don't have data:
The backend was updated to parse the JSON data from the `details` field. Make sure the backend is running the latest version (restarted above).

### To verify data exists:
```bash
docker-compose exec postgres psql -U frauduser -d frauddb -c "SELECT COUNT(*) FROM case_assignments;"
```

Should show 60 case assignments.

## Next Steps

1. **Review a few cases** to see the different data types
2. **Check the scoring** - each case has different risk scores
3. **Try classifying** a case as fraud or false positive
4. **Add notes** to explain your decision

## Available Test Cases

- **5 Transaction cases** - Various fraud patterns
- **4 Loan cases** - Income/application issues  
- **3 KYC cases** - Identity/document problems
- **2 Credit cases** - Score/history anomalies
- **2 Repayment cases** - Payment irregularities

Total: 15 flagged items with 60 case assignments (including duplicates for testing)

