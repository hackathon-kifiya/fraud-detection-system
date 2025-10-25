package com.frauddetection.domain;

import java.util.Map;
import java.util.HashMap;
import java.util.List;
import java.util.ArrayList;

/**
 * Dynamic fact class that can represent any data structure
 * This allows the rule engine to work with variable data without pre-modeled classes
 */
public class DynamicFact {
    private String entityId;
    private String dataType;
    private Map<String, Object> properties;
    private List<Violation> violations;

    public DynamicFact() {
        this.properties = new HashMap<>();
        this.violations = new ArrayList<>();
    }

    public DynamicFact(String entityId, String dataType) {
        this();
        this.entityId = entityId;
        this.dataType = dataType;
    }

    // Getters and Setters
    public String getEntityId() { return entityId; }
    public void setEntityId(String entityId) { this.entityId = entityId; }

    public String getDataType() { return dataType; }
    public void setDataType(String dataType) { this.dataType = dataType; }

    public Map<String, Object> getProperties() { return properties; }
    public void setProperties(Map<String, Object> properties) { this.properties = properties; }

    public List<Violation> getViolations() { return violations; }
    public void setViolations(List<Violation> violations) { this.violations = violations; }

    // Convenience methods for property access
    public void setProperty(String key, Object value) {
        this.properties.put(key, value);
    }

    public Object getProperty(String key) {
        return this.properties.get(key);
    }

    public String getStringProperty(String key) {
        Object value = getProperty(key);
        return value != null ? value.toString() : null;
    }

    public Double getDoubleProperty(String key) {
        Object value = getProperty(key);
        if (value instanceof Number) {
            return ((Number) value).doubleValue();
        }
        return null;
    }

    public Integer getIntProperty(String key) {
        Object value = getProperty(key);
        if (value instanceof Number) {
            return ((Number) value).intValue();
        }
        return null;
    }

    public Boolean getBooleanProperty(String key) {
        Object value = getProperty(key);
        if (value instanceof Boolean) {
            return (Boolean) value;
        }
        return null;
    }

    // Violation management
    public void addViolation(String code, int weight, String description) {
        this.violations.add(new Violation(code, weight, description));
    }

    public boolean hasViolations() {
        return !violations.isEmpty();
    }

    public int getViolationCount() {
        return violations.size();
    }

    public double getTotalRiskScore() {
        return violations.stream()
                .mapToDouble(Violation::getWeight)
                .sum();
    }

    @Override
    public String toString() {
        return "DynamicFact{" +
                "entityId='" + entityId + '\'' +
                ", dataType='" + dataType + '\'' +
                ", properties=" + properties +
                ", violationsCount=" + violations.size() +
                '}';
    }
}
