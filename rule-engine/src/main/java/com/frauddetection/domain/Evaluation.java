package com.frauddetection.domain;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Evaluation {
    private String entityId;
    private double riskScore;
    private List<Violation> violations;
    private EvaluationMetadata metadata;
}
