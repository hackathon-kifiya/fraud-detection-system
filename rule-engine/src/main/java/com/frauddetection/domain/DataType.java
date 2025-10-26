package com.frauddetection.domain;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.relational.core.mapping.Column;
import org.springframework.data.relational.core.mapping.Table;
import java.time.Instant;
import java.util.UUID;

/**
 * DataType domain entity representing a schema for dynamic data types.
 * Defines the structure and allowed fields for a specific type of data.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Table("data_type")
public class DataType {
    @Id
    private UUID id;
    
    @Column("data_type")
    private String dataType;
    private String name;
    private String description;
    
    /**
     * JSON schema definition as a Map.
     * Example: {
     *   "fields": {
     *     "amount": "Double",
     *     "merchant": "String",
     *     "timestamp": "Instant"
     *   },
     *   "required": ["amount", "merchant"]
     * }
     */
    @Column("schema_definition")
    private String schemaDefinition; // JSON string
    
    @Column("sample_data")
    private String sampleData; // JSON string
    
    private Status status;
    
    @Column("created_at")
    private Instant createdAt;
    
    @Column("updated_at")
    private Instant updatedAt;
    
    @Column("created_by")
    private String createdBy;
    
    @Column("updated_by")
    private String updatedBy;
    
    public enum Status {
        ACTIVE, INACTIVE, DRAFT
    }
}

