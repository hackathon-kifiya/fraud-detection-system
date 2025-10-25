package com.frauddetection.domain;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class EvaluationResponse {
    private String entityId;
    private double riskScore;
    private List<Violation> violations;
    private Verdict verdict;
    private Map<String, Object> metadata;

    public enum Verdict {
        PASS, REVIEW, FAIL
    }

    // Constructor
    public EvaluationResponse(String entityId, double riskScore, List<Violation> violations, Verdict verdict) {
        this.entityId = entityId;
        this.riskScore = riskScore;
        this.violations = violations;
        this.verdict = verdict;
    }
}
