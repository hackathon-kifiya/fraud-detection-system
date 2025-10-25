package com.frauddetection.domain;

import java.util.List;
import java.util.Map;

public class EvaluationRequest {
    private DataType dataType;
    private List<Map<String, Object>> facts;

    public enum DataType {
        TRANSACTION, KYC, LOAN, CREDIT, REPAYMENT
    }

    // Default constructor
    public EvaluationRequest() {}

    // Constructor
    public EvaluationRequest(DataType dataType, List<Map<String, Object>> facts) {
        this.dataType = dataType;
        this.facts = facts;
    }

    // Getters and Setters
    public DataType getDataType() { return dataType; }
    public void setDataType(DataType dataType) { this.dataType = dataType; }

    public List<Map<String, Object>> getFacts() { return facts; }
    public void setFacts(List<Map<String, Object>> facts) { this.facts = facts; }

    @Override
    public String toString() {
        return "EvaluationRequest{" +
                "dataType=" + dataType +
                ", factsCount=" + (facts != null ? facts.size() : 0) +
                '}';
    }
}
