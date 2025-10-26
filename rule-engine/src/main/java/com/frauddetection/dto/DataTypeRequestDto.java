package com.frauddetection.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/**
 * Request DTO for creating and updating data types.
 * 
 * Schema definition structure example:
 * {
 *   "fields": {
 *     "amount": "Double",
 *     "merchant": "String",
 *     "timestamp": "Instant"
 *   },
 *   "required": ["amount", "merchant"],
 *   "validationRules": {
 *     "amount": {"min": 0, "max": 1000000},
 *     "merchant": {"pattern": "^[A-Za-z0-9\\s]+$"}
 *   }
 * }
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class DataTypeRequestDto {
    private String dataType;
    private String name;
    private String description;
    
    /**
     * Schema definition as a flexible Map.
     * Can contain:
     * - "fields": Map<String, String> - field names to types
     * - "required": List<String> - required field names
     * - "validationRules": Map<String, Map> - validation rules per field
     * - Any other metadata
     */
    private Map<String, Object> schemaDefinition;
    
    /**
     * Sample data as a Map for validation and documentation.
     */
    private Map<String, Object> sampleData;
    
    private String createdBy;
    private String updatedBy;
}

