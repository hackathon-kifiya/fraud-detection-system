package com.frauddetection.domain;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

public class KYC {
    private String userId;
    private boolean verifiedStatus;
    private Instant verificationTimestamp;

    private final List<Violation> violations = new ArrayList<>();

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }
    public boolean isVerifiedStatus() { return verifiedStatus; }
    public void setVerifiedStatus(boolean verifiedStatus) { this.verifiedStatus = verifiedStatus; }
    public Instant getVerificationTimestamp() { return verificationTimestamp; }
    public void setVerificationTimestamp(Instant verificationTimestamp) { this.verificationTimestamp = verificationTimestamp; }

    public List<Violation> getViolations() { return violations; }
    public void addViolation(String code, int weight, String description) {
        this.violations.add(new Violation(code, weight, description));
    }
}


