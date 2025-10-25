package com.frauddetection.domain;

import java.time.Instant;
import java.util.UUID;

public class Rule {
    private UUID id;
    private String name;
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

    // Default constructor
    public Rule() {}

    // Constructor for creating new rules
    public Rule(String name, DataType dataType, String drlContent, String createdBy) {
        this.name = name;
        this.dataType = dataType;
        this.drlContent = drlContent;
        this.createdBy = createdBy;
        this.version = 1;
        this.status = Status.DRAFT;
        this.createdAt = Instant.now();
        this.updatedAt = Instant.now();
    }

    // Getters and Setters
    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public DataType getDataType() { return dataType; }
    public void setDataType(DataType dataType) { this.dataType = dataType; }

    public String getDrlContent() { return drlContent; }
    public void setDrlContent(String drlContent) { this.drlContent = drlContent; }

    public Integer getVersion() { return version; }
    public void setVersion(Integer version) { this.version = version; }

    public Status getStatus() { return status; }
    public void setStatus(Status status) { this.status = status; }

    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }

    public Instant getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(Instant updatedAt) { this.updatedAt = updatedAt; }

    public String getCreatedBy() { return createdBy; }
    public void setCreatedBy(String createdBy) { this.createdBy = createdBy; }

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
