package com.frauddetection.domain;

import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.util.Map;
import java.util.HashMap;
import java.util.List;
import java.util.ArrayList;

/**
 * Dynamic fact class that can represent any data structure
 * This allows the rule engine to work with variable data without pre-modeled classes
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DynamicFact {
    private String entityId;
    private String dataType;
    @Builder.Default
    private Map<String, Object> properties = new HashMap<>();
    @Builder.Default
    private List<Violation> violations = new ArrayList<>();
    @Builder.Default
    private double riskScore = 0.0;
    
    // Constructor for convenience when creating without builder
    public DynamicFact(String entityId, String dataType) {
        this.entityId = entityId;
        this.dataType = dataType;
        this.properties = new HashMap<>();
        this.violations = new ArrayList<>();
    }
    
    // Method to set a property dynamically
    public void setProperty(String key, Object value) {
        if (properties == null) {
            properties = new HashMap<>();
        }
        properties.put(key, value);
    }
    
    // Method to set risk score
    public void setRiskScore(double score) {
        this.riskScore = score;
    }
    
    // Method to get risk score
    public double getRiskScore() {
        return this.riskScore;
    }
    
    // Method to get total risk score from violations
    public double getTotalRiskScore() {
        if (violations == null || violations.isEmpty()) {
            return riskScore;
        }
        return riskScore + violations.stream()
                .mapToInt(Violation::getWeight)
                .sum();
    }
    
    // Method to add a violation
    public void addViolation(String code, String description) {
        if (violations == null) {
            violations = new ArrayList<>();
        }
        violations.add(Violation.builder()
                .code(code)
                .description(description)
                .weight(1) // default weight
                .build());
    }
    
    // Method to add a violation with weight
    public void addViolation(String code, String description, int weight) {
        if (violations == null) {
            violations = new ArrayList<>();
        }
        violations.add(Violation.builder()
                .code(code)
                .description(description)
                .weight(weight)
                .build());
    }
    
    // Helper method to get a property as a Number for DRL rules
    public Number getPropertyAsNumber(String key) {
        Object value = properties.get(key);
        if (value instanceof Number) {
            return (Number) value;
        }
        return 0.0;
    }
    
    // Helper method to get a property as a String for DRL rules
    public String getPropertyAsString(String key) {
        Object value = properties.get(key);
        if (value != null) {
            return value.toString();
        }
        return "";
    }
    
    // Helper method to check if a property exists
    public boolean hasProperty(String key) {
        return properties != null && properties.containsKey(key);
    }
}
