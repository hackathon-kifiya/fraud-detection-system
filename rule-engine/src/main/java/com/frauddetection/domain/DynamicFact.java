package com.frauddetection.domain;

import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.experimental.SuperBuilder;

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
@SuperBuilder
public class DynamicFact {
    private String entityId;
    private String dataType;
    private Map<String, Object> properties = new HashMap<>();
    private List<Violation> violations = new ArrayList<>();
}
