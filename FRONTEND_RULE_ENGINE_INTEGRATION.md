# Frontend Rule Engine Integration Plan

## Overview
Integrate the rule management engine APIs into the frontend to enable administrators to create, manage, test, and monitor fraud detection rules dynamically without code deployment.

## Use Cases

### 1. Admin Rule Management
**Who:** System administrators and fraud analysts  
**What:** Create, update, activate/deactivate, and version control fraud detection rules  
**Why:** Enable business users to adjust fraud detection logic without developer intervention

### 2. Rule Testing & Validation
**Who:** Fraud analysts and QA teams  
**What:** Test rules against sample data before activation  
**Why:** Ensure rules work correctly and don't produce false positives/negatives

### 3. Rule Performance Monitoring
**Who:** System administrators  
**What:** View rule execution statistics, violation rates, and impact analysis  
**Why:** Optimize rule effectiveness and identify problematic rules

### 4. Real-time Data Evaluation
**Who:** Auditors and fraud investigators  
**What:** Manually evaluate specific transactions/data against active rules  
**Why:** Investigate suspicious cases and understand why items were flagged

---

## Implementation Components

### A. API Service Layer (`frontend/src/services/api.js`)

Add new `ruleEngineAPI` object with methods:

#### Rule Management:
```javascript
export const ruleEngineAPI = {
  // Rule CRUD operations
  createRule: (data) => api.post('/api/rules', data),
  getAllRules: (params) => api.get('/api/rules', { params }),
  getRule: (id) => api.get(`/api/rules/${id}`),
  updateRule: (id, data) => api.put(`/api/rules/${id}`, data),
  deleteRule: (id) => api.delete(`/api/rules/${id}`),
  
  // Rule activation
  activateRule: (id) => api.post(`/api/rules/${id}/activate`),
  deactivateRule: (id) => api.post(`/api/rules/${id}/deactivate`),
  
  // Rule validation and versioning
  validateDrl: (data) => api.post('/api/rules/validate', data),
  getRuleVersions: (id) => api.get(`/api/rules/${id}/versions`),
  rollbackRule: (id, version, data) => api.post(`/api/rules/${id}/rollback/${version}`, data),
  
  // Rule evaluation
  evaluateTransaction: (facts) => api.post('/api/evaluate/transaction', { facts }),
  evaluateKYC: (facts) => api.post('/api/evaluate/kyc', { facts }),
  evaluateLoan: (facts) => api.post('/api/evaluate/loan', { facts }),
  evaluateCredit: (facts) => api.post('/api/evaluate/credit', { facts }),
  evaluateRepayment: (facts) => api.post('/api/evaluate/repayment', { facts }),
  evaluateGeneric: (dataType, facts) => api.post('/api/evaluate/generic', { dataType, facts }),
};
```

---

### B. New Components

#### 1. RuleManagementPage.js
**Location:** `frontend/src/components/RuleManagementPage.js`

**Features:**
- Rule list with filtering by data type and status
- Create new rule button (opens dialog)
- Rule cards showing: name, data type, status, version, last updated
- Quick actions: activate/deactivate, edit, delete, view versions
- Search and filter capabilities
- Pagination for large rule sets

**Layout:**
```
┌─────────────────────────────────────────────┐
│  Rule Management                   [+ New]  │
├─────────────────────────────────────────────┤
│  [All Types ▼] [All Status ▼] [Search...]  │
├─────────────────────────────────────────────┤
│  ┌──────────────────────────────────────┐  │
│  │ High Amount Transaction Rule    [⚡]  │  │
│  │ Transaction • Active • v3             │  │
│  │ Updated: 2 days ago                   │  │
│  │ [Edit] [Deactivate] [Versions] [⋮]   │  │
│  └──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────┐  │
│  │ Unverified KYC Rule            [💤]  │  │
│  │ KYC • Inactive • v1                   │  │
│  │ Updated: 1 week ago                   │  │
│  │ [Edit] [Activate] [Versions] [⋮]     │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

**Key Props:**
- `onShowSnackbar`: Function to show notifications

**State Management:**
- `rules`: Array of rule objects
- `filters`: { dataType, status, search }
- `loading`: Boolean
- `selectedRule`: Currently selected rule for actions

---

#### 2. RuleEditorDialog.js
**Location:** `frontend/src/components/RuleEditorDialog.js`

**Features:**
- Full-screen dialog for creating/editing rules
- Form fields: name, data type selector, DRL content (code editor)
- Syntax highlighting for DRL code (use Monaco Editor or CodeMirror)
- Real-time validation as user types
- Sample DRL templates for each data type
- Test rule button (opens test panel)
- Save as draft or activate immediately
- Change description field for updates

**Layout:**
```
┌──────────────────────────────────────────────┐
│  Create New Rule                      [X]    │
├──────────────────────────────────────────────┤
│  Rule Name: [_________________________]      │
│  Data Type: [Transaction ▼]                  │
│  Status: [Draft ▼]                           │
│                                              │
│  DRL Content:                                │
│  ┌────────────────────────────────────────┐ │
│  │ package rules;                         │ │
│  │                                        │ │
│  │ import com.frauddetection.domain...   │ │
│  │                                        │ │
│  │ rule "My Rule"                         │ │
│  │ when                                   │ │
│  │     $f: DynamicFact(...)              │ │
│  │ then                                   │ │
│  │     $f.addViolation(...)              │ │
│  │ end                                    │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  [Load Template] [Validate] [Test Rule]     │
│  ✓ Validation passed                         │
│                                              │
│  [Cancel]              [Save Draft] [Save]   │
└──────────────────────────────────────────────┘
```

**Key Props:**
- `open`: Boolean to control dialog visibility
- `rule`: Rule object for editing (null for new rule)
- `onClose`: Callback when dialog closes
- `onSave`: Callback when rule is saved

---

#### 3. RuleTestPanel.js
**Location:** `frontend/src/components/RuleTestPanel.js`

**Features:**
- JSON editor for inputting test facts
- Sample data templates for each data type
- Execute test button
- Results display: risk score, violations, verdict
- Multiple test cases support
- Save test cases for regression testing

**Layout:**
```
┌──────────────────────────────────────────────┐
│  Test Rule: High Amount Transaction Rule     │
├──────────────────────────────────────────────┤
│  Test Data (JSON):                           │
│  ┌────────────────────────────────────────┐ │
│  │ {                                      │ │
│  │   "entityId": "test-123",             │ │
│  │   "amount": 15000,                    │ │
│  │   "accountBalance": 5000              │ │
│  │ }                                      │ │
│  └────────────────────────────────────────┘ │
│  [Load Sample] [Execute Test]                │
│                                              │
│  Results:                                    │
│  ┌────────────────────────────────────────┐ │
│  │ ✓ Test Passed                          │ │
│  │ Risk Score: 35                         │ │
│  │ Verdict: REVIEW                        │ │
│  │ Violations:                            │ │
│  │  • TXN_HIGH_VS_BAL (20 pts)           │ │
│  │  • TXN_HIGH_AMOUNT (15 pts)           │ │
│  └────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

**Key Props:**
- `rule`: Rule object to test
- `dataType`: Data type for the test
- `onClose`: Callback when panel closes

---

#### 4. RuleVersionHistoryDialog.js
**Location:** `frontend/src/components/RuleVersionHistoryDialog.js`

**Features:**
- Timeline view of all rule versions
- Show version number, date, author, change description
- View DRL content for each version
- Diff view between versions
- Rollback button for each version
- Export version history

**Key Props:**
- `open`: Boolean to control dialog visibility
- `ruleId`: ID of the rule to show versions for
- `onClose`: Callback when dialog closes
- `onRollback`: Callback when version is rolled back

---

#### 5. DataEvaluationPanel.js
**Location:** `frontend/src/components/DataEvaluationPanel.js`

**Features:**
- Standalone evaluation tool for auditors
- Select data type
- Input data (JSON or form)
- Execute evaluation against active rules
- Display detailed results with all violations
- Export results
- Link to flagged items if applicable

**Key Props:**
- `onShowSnackbar`: Function to show notifications

---

#### 6. RuleDashboard.js (Widget for main Dashboard)
**Location:** `frontend/src/components/RuleDashboard.js`

**Features:**
- Summary statistics: total rules, active rules, by data type
- Recent rule changes
- Top triggering rules
- Rule health indicators
- Quick links to rule management

**Key Props:**
- `onShowSnackbar`: Function to show notifications

---

### C. Navigation Updates

Update `App.js` to add new menu section:

```javascript
{/* Rule Management Section - Admin only */}
{user?.role === 'admin' && (
  <Box sx={{ mb: 3 }}>
    <Typography 
      variant="caption" 
      sx={{ 
        color: '#9e9e9e', 
        px: 3, 
        py: 1, 
        display: 'block',
        fontWeight: 'bold',
        letterSpacing: '0.5px'
      }}
    >
      RULE ENGINE
    </Typography>
    <List sx={{ px: 1 }}>
      <ListItem disablePadding sx={{ mb: 0.5 }}>
        <ListItemButton
          component="a"
          href="/rules"
          sx={{
            borderRadius: 1,
            mx: 1,
            '&:hover': { bgcolor: '#616161' },
          }}
        >
          <ListItemIcon sx={{ color: 'white', minWidth: 40 }}>
            <StorageIcon />
          </ListItemIcon>
          <ListItemText 
            primary="Manage Rules" 
            sx={{ 
              color: 'white',
              '& .MuiListItemText-primary': {
                fontSize: '0.9rem',
                fontWeight: 'bold'
              }
            }} 
          />
        </ListItemButton>
      </ListItem>
      <ListItem disablePadding sx={{ mb: 0.5 }}>
        <ListItemButton
          component="a"
          href="/rules/evaluate"
          sx={{
            borderRadius: 1,
            mx: 1,
            '&:hover': { bgcolor: '#616161' },
          }}
        >
          <ListItemIcon sx={{ color: 'white', minWidth: 40 }}>
            <SpeedIcon />
          </ListItemIcon>
          <ListItemText 
            primary="Test Evaluation" 
            sx={{ 
              color: 'white',
              '& .MuiListItemText-primary': {
                fontSize: '0.9rem',
                fontWeight: 'bold'
              }
            }} 
          />
        </ListItemButton>
      </ListItem>
    </List>
  </Box>
)}
```

---

### D. Integration with Existing Pages

#### Update TransactionsPage.js, LoanRequestsPage.js, etc.
Add "Evaluate with Rules" button that:
1. Takes selected row data
2. Converts to evaluation request format
3. Calls rule engine evaluation API
4. Shows results in dialog

Example implementation:
```javascript
const handleEvaluateWithRules = async (rowData) => {
  try {
    const facts = [{
      entityId: rowData.id,
      amount: rowData.amount,
      accountBalance: rowData.accountBalance,
      // ... other properties
    }];
    
    const response = await ruleEngineAPI.evaluateTransaction(facts);
    
    // Show results in dialog
    setEvaluationResults(response.data.response);
    setEvaluationDialogOpen(true);
  } catch (error) {
    onShowSnackbar('Failed to evaluate data: ' + error.message, 'error');
  }
};
```

#### Update Dashboard.js
Add RuleDashboard widget showing rule statistics

#### Update SettingsPage.js
Add rule engine health check to system status:
```javascript
const checkRuleEngineHealth = async () => {
  try {
    const response = await api.get('http://localhost:8082/health');
    return response.status === 200 ? 'healthy' : 'unhealthy';
  } catch (error) {
    return 'error';
  }
};
```

---

### E. Route Configuration

Add new routes in `App.js`:
```javascript
<Route 
  path="/rules" 
  element={<RuleManagementPage onShowSnackbar={showSnackbar} />} 
/>
<Route 
  path="/rules/evaluate" 
  element={<DataEvaluationPanel onShowSnackbar={showSnackbar} />} 
/>
```

---

## User Workflows

### Workflow 1: Create New Rule
1. Admin navigates to Rule Management page
2. Clicks "+ New Rule" button
3. Fills in rule name, selects data type
4. Loads DRL template or writes custom DRL
5. Clicks "Validate" to check syntax
6. Clicks "Test Rule" to test with sample data
7. Reviews test results
8. Saves as draft or activates immediately
9. Rule is stored in database with version 1

### Workflow 2: Update Existing Rule
1. Admin finds rule in list
2. Clicks "Edit" button
3. Modifies DRL content
4. Validates and tests changes
5. Enters change description
6. Saves - creates new version
7. Old version archived in version history

### Workflow 3: Test Data Against Rules
1. Auditor navigates to Test Evaluation page
2. Selects data type (e.g., Transaction)
3. Inputs JSON data or uses form
4. Clicks "Evaluate"
5. Views risk score, violations, and verdict
6. Can export results or link to create flagged item

### Workflow 4: Rollback Rule
1. Admin opens rule version history
2. Reviews past versions
3. Selects version to rollback to
4. Confirms rollback
5. New version created with old content
6. Rule immediately uses rolled-back logic

### Workflow 5: Monitor Rule Performance
1. Admin views Rule Dashboard
2. Sees which rules trigger most frequently
3. Identifies rules causing false positives
4. Deactivates or modifies problematic rules
5. Tracks improvement over time

---

## Sample DRL Templates

Provide templates for each data type to help users:

### Transaction Template:
```drl
package rules;

import com.frauddetection.domain.DynamicFact;

rule "High Amount Transaction"
when
    $f: DynamicFact(
        dataType == "transaction",
        getDoubleProperty("amount") > 10000
    )
then
    $f.addViolation("TXN_HIGH_AMOUNT", 20, "Transaction amount exceeds threshold");
end
```

### KYC Template:
```drl
package rules;

import com.frauddetection.domain.DynamicFact;

rule "Unverified KYC"
when
    $f: DynamicFact(
        dataType == "kyc",
        getBooleanProperty("verifiedStatus") == false
    )
then
    $f.addViolation("KYC_UNVERIFIED", 15, "User is not KYC verified");
end
```

### Loan Template:
```drl
package rules;

import com.frauddetection.domain.DynamicFact;

rule "High Risk Loan"
when
    $f: DynamicFact(
        dataType == "loan",
        getDoubleProperty("amount") > 50000
    )
then
    $f.addViolation("LOAN_HIGH_AMOUNT", 25, "Loan amount exceeds high risk threshold");
end
```

### Credit Template:
```drl
package rules;

import com.frauddetection.domain.DynamicFact;

rule "Low Credit Score"
when
    $f: DynamicFact(
        dataType == "credit",
        getIntProperty("score") < 600
    )
then
    $f.addViolation("CREDIT_LOW_SCORE", 30, "Credit score below acceptable threshold");
end
```

### Repayment Template:
```drl
package rules;

import com.frauddetection.domain.DynamicFact;

rule "Late Repayment"
when
    $f: DynamicFact(
        dataType == "repayment",
        getBooleanProperty("isLate") == true
    )
then
    $f.addViolation("REPAYMENT_LATE", 25, "Repayment is late");
end
```

---

## Technical Considerations

### State Management
- Use React Context or Redux for rule management state
- Cache active rules to reduce API calls
- Real-time updates when rules change

### Code Editor
- Use Monaco Editor (VS Code editor) for DRL editing
- Add custom DRL syntax highlighting
- Auto-completion for DynamicFact methods

### Validation Feedback
- Show validation errors inline
- Highlight problematic lines in code editor
- Provide helpful error messages

### Performance
- Lazy load rule editor components
- Paginate rule lists
- Debounce validation API calls

### Security
- Only admins can create/modify rules
- Audit log all rule changes
- Require confirmation for destructive actions

---

## API Request/Response Examples

### Create Rule Request:
```json
POST /api/rules
{
  "name": "High Amount Transaction Rule",
  "dataType": "TRANSACTION",
  "drlContent": "package rules;\n\nimport com.frauddetection.domain.DynamicFact;\n\nrule \"High amount\"\nwhen\n    $f: DynamicFact(dataType == \"transaction\", getDoubleProperty(\"amount\") > 10000)\nthen\n    $f.addViolation(\"HIGH_AMOUNT\", 15, \"Amount exceeds threshold\");\nend",
  "createdBy": "admin@example.com"
}
```

### Create Rule Response:
```json
{
  "success": true,
  "message": "Rule created successfully",
  "rule": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "High Amount Transaction Rule",
    "dataType": "TRANSACTION",
    "version": 1,
    "status": "DRAFT",
    "createdAt": "2025-10-25T10:30:00Z",
    "updatedAt": "2025-10-25T10:30:00Z",
    "createdBy": "admin@example.com"
  }
}
```

### Evaluate Transaction Request:
```json
POST /api/evaluate/transaction
{
  "facts": [
    {
      "entityId": "txn-123",
      "amount": 15000.0,
      "accountBalance": 5000.0,
      "type": "debit",
      "paymentMethod": "card"
    }
  ]
}
```

### Evaluate Transaction Response:
```json
{
  "success": true,
  "response": {
    "entityId": "txn-123",
    "riskScore": 35.0,
    "verdict": "REVIEW",
    "violations": [
      {
        "code": "TXN_HIGH_VS_BAL",
        "weight": 20,
        "description": "Transaction amount exceeds 2x account balance"
      },
      {
        "code": "TXN_HIGH_AMOUNT",
        "weight": 15,
        "description": "Transaction amount exceeds high threshold"
      }
    ]
  }
}
```

---

## Benefits

1. **No Code Deployments:** Business users update rules without engineering
2. **Faster Response:** Quickly adapt to new fraud patterns
3. **Version Control:** Complete audit trail of all changes
4. **Testing:** Validate rules before production use
5. **Transparency:** Clear visibility into active fraud detection logic
6. **Flexibility:** Support for any data structure via DynamicFact
7. **Empowerment:** Fraud analysts can iterate on detection logic independently
8. **Reduced Risk:** Test rules thoroughly before activating
9. **Compliance:** Full audit trail for regulatory requirements
10. **Cost Savings:** Reduce engineering time for rule adjustments

---

## Implementation Timeline

### Phase 1: Core Infrastructure (Week 1)
- Add ruleEngineAPI to api.js
- Create RuleManagementPage with basic list view
- Add navigation menu items

### Phase 2: Rule Editor (Week 2)
- Implement RuleEditorDialog with code editor
- Add DRL templates
- Implement validation integration

### Phase 3: Testing & Evaluation (Week 3)
- Create RuleTestPanel
- Implement DataEvaluationPanel
- Add evaluation to existing data pages

### Phase 4: Advanced Features (Week 4)
- Create RuleVersionHistoryDialog
- Add RuleDashboard widget
- Implement rule performance monitoring

### Phase 5: Polish & Testing (Week 5)
- UI/UX improvements
- Integration testing
- Documentation and training materials

---

## Dependencies

### NPM Packages to Install:
```bash
npm install @monaco-editor/react  # Code editor
npm install react-json-view        # JSON viewer/editor
npm install date-fns               # Date formatting
```

---

## Success Metrics

1. **Adoption Rate:** % of fraud rules managed through UI vs. code
2. **Time to Deploy:** Average time from rule creation to production
3. **Rule Quality:** % of rules that pass validation on first try
4. **False Positive Reduction:** Improvement in false positive rate
5. **User Satisfaction:** Feedback from fraud analysts and admins

---

## Future Enhancements

1. **Rule Templates Library:** Pre-built rules for common fraud patterns
2. **A/B Testing:** Test multiple rule versions simultaneously
3. **Machine Learning Integration:** Suggest rule improvements based on data
4. **Bulk Operations:** Import/export rules, bulk activate/deactivate
5. **Rule Scheduling:** Activate rules at specific times
6. **Collaboration Features:** Comments, reviews, approvals
7. **Advanced Analytics:** Rule effectiveness dashboard
8. **Natural Language Rules:** Convert plain English to DRL
