package com.frauddetection.domain;

import lombok.Data;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Data
public class Transaction {
    private UUID txnId;
    private String userId;
    private double amount;
    private Instant timestamp;
    private String type; // credit/debit
    private String paymentMethod;
    private double accountBalance;

    private final List<Violation> violations = new ArrayList<>();

    public void addViolation(String code, int weight, String description) {
        this.violations.add(new Violation(code, weight, description));
    }
}


