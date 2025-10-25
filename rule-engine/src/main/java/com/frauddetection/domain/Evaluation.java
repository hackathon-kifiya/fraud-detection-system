package com.frauddetection.domain;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@SuperBuilder
public class Evaluation {
    private String entityId;
    private double riskScore;
    private List<Violation> violations;
    private EvaluationMetadata metadata;
}
