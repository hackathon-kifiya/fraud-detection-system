package com.frauddetection.domain;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class LoanRequest {
    private UUID loanId;
    private String userId;
    private double amountRequested;
    private String purpose;
    private Instant requestTimestamp;

    private final List<Violation> violations = new ArrayList<>();

    public UUID getLoanId() { return loanId; }
    public void setLoanId(UUID loanId) { this.loanId = loanId; }
    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }
    public double getAmountRequested() { return amountRequested; }
    public void setAmountRequested(double amountRequested) { this.amountRequested = amountRequested; }
    public String getPurpose() { return purpose; }
    public void setPurpose(String purpose) { this.purpose = purpose; }
    public Instant getRequestTimestamp() { return requestTimestamp; }
    public void setRequestTimestamp(Instant requestTimestamp) { this.requestTimestamp = requestTimestamp; }

    public List<Violation> getViolations() { return violations; }
    public void addViolation(String code, int weight, String description) {
        this.violations.add(new Violation(code, weight, description));
    }
}


