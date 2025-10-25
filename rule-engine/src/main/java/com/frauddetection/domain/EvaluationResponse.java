package com.frauddetection.domain;

import java.util.List;
import java.util.Map;

public class EvaluationResponse {
    private String entityId;
    private double riskScore;
    private List<Violation> violations;
    private Verdict verdict;
    private Map<String, Object> metadata;

    public enum Verdict {
        APPROVE, REVIEW, REJECT
    }

    // Default constructor
    public EvaluationResponse() {}

    // Constructor
    public EvaluationResponse(String entityId, double riskScore, List<Violation> violations, Verdict verdict) {
        this.entityId = entityId;
        this.riskScore = riskScore;
        this.violations = violations;
        this.verdict = verdict;
    }

    // Getters and Setters
    public String getEntityId() { return entityId; }
    public void setEntityId(String entityId) { this.entityId = entityId; }

    public double getRiskScore() { return riskScore; }
    public void setRiskScore(double riskScore) { this.riskScore = riskScore; }

    public List<Violation> getViolations() { return violations; }
    public void setViolations(List<Violation> violations) { this.violations = violations; }

    public Verdict getVerdict() { return verdict; }
    public void setVerdict(Verdict verdict) { this.verdict = verdict; }

    public Map<String, Object> getMetadata() { return metadata; }
    public void setMetadata(Map<String, Object> metadata) { this.metadata = metadata; }

    @Override
    public String toString() {
        return "EvaluationResponse{" +
                "entityId='" + entityId + '\'' +
                ", riskScore=" + riskScore +
                ", verdict=" + verdict +
                ", violationsCount=" + (violations != null ? violations.size() : 0) +
                '}';
    }
}
