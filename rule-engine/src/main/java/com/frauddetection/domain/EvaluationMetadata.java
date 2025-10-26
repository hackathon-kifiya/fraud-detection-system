package com.frauddetection.domain;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class EvaluationMetadata {
    private Integer totalFacts;
    private Double totalRiskScore;
    private Double averageRiskScore;
    private Double normalizedRiskScore;
    private Integer totalViolations;
    private Integer individualResponses;
}
