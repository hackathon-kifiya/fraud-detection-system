package com.frauddetection.domain;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class Repayment {
    private UUID repaymentId;
    private String userId;
    private UUID loanId;
    private double amount;
    private Instant timestamp;
    private String status; // paid/late/default

    private final List<Violation> violations = new ArrayList<>();

    public UUID getRepaymentId() { return repaymentId; }
    public void setRepaymentId(UUID repaymentId) { this.repaymentId = repaymentId; }
    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }
    public UUID getLoanId() { return loanId; }
    public void setLoanId(UUID loanId) { this.loanId = loanId; }
    public double getAmount() { return amount; }
    public void setAmount(double amount) { this.amount = amount; }
    public Instant getTimestamp() { return timestamp; }
    public void setTimestamp(Instant timestamp) { this.timestamp = timestamp; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public List<Violation> getViolations() { return violations; }
    public void addViolation(String code, int weight, String description) {
        this.violations.add(new Violation(code, weight, description));
    }
}


