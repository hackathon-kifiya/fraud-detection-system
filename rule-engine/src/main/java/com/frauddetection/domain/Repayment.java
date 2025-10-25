package com.frauddetection.domain;

import lombok.Data;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Data
public class Repayment {
    private UUID repaymentId;
    private String userId;
    private UUID loanId;
    private double amount;
    private Instant timestamp;
    private String status; // paid/late/default

    private final List<Violation> violations = new ArrayList<>();

    public void addViolation(String code, int weight, String description) {
        this.violations.add(new Violation(code, weight, description));
    }
}


