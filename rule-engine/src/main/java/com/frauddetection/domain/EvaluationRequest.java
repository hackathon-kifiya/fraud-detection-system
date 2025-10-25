package com.frauddetection.domain;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

@Data
public class EvaluationRequest {
    private DataType dataType;
    private List<Map<String, Object>> facts;

    public enum DataType {
        TRANSACTION, KYC, LOAN, CREDIT, REPAYMENT
    }

    // Constructor
    public EvaluationRequest(DataType dataType, List<Map<String, Object>> facts) {
        this.dataType = dataType;
        this.facts = facts;
    }
}
