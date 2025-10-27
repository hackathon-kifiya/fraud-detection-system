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

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Table("rule")
public class Rule {
    @Id
    private UUID id;
    
    private String name;
    private String description;
    @Column("data_type")
    private String dataType;
    @Column("drl_content")
    private String drlContent;
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
