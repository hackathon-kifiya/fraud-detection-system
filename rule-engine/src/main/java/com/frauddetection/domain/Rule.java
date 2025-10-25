package com.frauddetection.domain;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.UUID;
@Data
@AllArgsConstructor
public class Rule {
    private UUID id;
    private String name;
    private String description;
    private DataType dataType;
    private String drlContent;
    private Integer version;
    private Status status;
    private Instant createdAt;
    private Instant updatedAt;
    private String createdBy;

    public enum DataType {
        TRANSACTION, KYC, LOAN, CREDIT, REPAYMENT
    }

    public enum Status {
        ACTIVE, INACTIVE, DRAFT
    }

    // Constructor for creating new rules
    public Rule(String name, String description, DataType dataType, String drlContent, String createdBy) {
        this.name = name;
        this.description = description;
        this.dataType = dataType;
        this.drlContent = drlContent;
        this.createdBy = createdBy;
        this.version = 1;
        this.status = Status.DRAFT;
        this.createdAt = Instant.now();
        this.updatedAt = Instant.now();
    }
}
