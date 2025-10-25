package com.frauddetection.domain;

import lombok.Data;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Data
public class LoanRequest {
    private UUID loanId;
    private String userId;
    private double amountRequested;
    private String purpose;
    private Instant requestTimestamp;

    private final List<Violation> violations = new ArrayList<>();

    public void addViolation(String code, int weight, String description) {
        this.violations.add(new Violation(code, weight, description));
    }
}


