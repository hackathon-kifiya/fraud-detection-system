package com.frauddetection.domain;

import lombok.Data;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

@Data
public class CreditHistory {
    private String userId;
    private int creditScore;
    private int defaultsCount;
    private Instant updatedAt;

    private final List<Violation> violations = new ArrayList<>();

    public void addViolation(String code, int weight, String description) {
        this.violations.add(new Violation(code, weight, description));
    }
}


