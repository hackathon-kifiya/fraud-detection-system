package com.frauddetection.domain;

import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.Instant;
import java.util.UUID;

@Data
@NoArgsConstructor
public class Rule {
    private UUID id;
    private String name;
    private String dataType;
    private String drlContent;
    private Integer version;
    private Status status;
    private Instant createdAt;
    private Instant updatedAt;
    private String createdBy;

    public enum Status {
        ACTIVE, INACTIVE, DRAFT
    }

    // Constructor for creating new rules
    public Rule(String name, String dataType, String drlContent, String createdBy) {
        this.name = name;
        this.dataType = dataType;
        this.drlContent = drlContent;
        this.createdBy = createdBy;
        this.version = 1;
        this.status = Status.DRAFT;
        this.createdAt = Instant.now();
        this.updatedAt = Instant.now();
    }

    @Override
    public String toString() {
        return "Rule{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", dataType=" + dataType +
                ", version=" + version +
                ", status=" + status +
                ", createdBy='" + createdBy + '\'' +
                '}';
    }
}
