package com.frauddetection.domain;

import lombok.Data;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

@Data
public class KYC {
    private String userId;
    private boolean verifiedStatus;
    private Instant verificationTimestamp;

    private final List<Violation> violations = new ArrayList<>();

    public void addViolation(String code, int weight, String description) {
        this.violations.add(new Violation(code, weight, description));
    }
}


