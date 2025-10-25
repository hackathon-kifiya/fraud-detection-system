package com.frauddetection.domain;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@SuperBuilder
public class EvaluationMetadata {
    private Integer totalFacts;
    private Double totalRiskScore;
    private Double averageRiskScore;
    private Integer totalViolations;
    private Integer individualResponses;
}
