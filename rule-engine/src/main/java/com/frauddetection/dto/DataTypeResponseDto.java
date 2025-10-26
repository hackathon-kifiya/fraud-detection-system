package com.frauddetection.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.Map;
import java.util.UUID;

/**
 * Response DTO for data type operations.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class DataTypeResponseDto {
    private UUID id;
    private String dataType;
    private String name;
    private String description;
    
    /**
     * Schema definition as a flexible Map.
     */
    private Map<String, Object> schemaDefinition;
    
    /**
     * Sample data as a Map.
     */
    private Map<String, Object> sampleData;
    
    private String status;
    private Instant createdAt;
    private Instant updatedAt;
    private String createdBy;
    private String updatedBy;
}

