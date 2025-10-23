package com.frauddetection.domain;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

public class CreditHistory {
    private String userId;
    private int creditScore;
    private int defaultsCount;
    private Instant updatedAt;

    private final List<Violation> violations = new ArrayList<>();

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }
    public int getCreditScore() { return creditScore; }
    public void setCreditScore(int creditScore) { this.creditScore = creditScore; }
    public int getDefaultsCount() { return defaultsCount; }
    public void setDefaultsCount(int defaultsCount) { this.defaultsCount = defaultsCount; }
    public Instant getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(Instant updatedAt) { this.updatedAt = updatedAt; }

    public List<Violation> getViolations() { return violations; }
    public void addViolation(String code, int weight, String description) {
        this.violations.add(new Violation(code, weight, description));
    }
}


