package com.frauddetection.domain;

import java.time.Instant;
import java.util.UUID;

public class RuleVersion {
    private UUID id;
    private UUID ruleId;
    private Integer version;
    private String drlContent;
    private String changeDescription;
    private Instant createdAt;
    private String createdBy;

    // Default constructor
    public RuleVersion() {}

    // Constructor for creating new versions
    public RuleVersion(UUID ruleId, Integer version, String drlContent, String changeDescription, String createdBy) {
        this.ruleId = ruleId;
        this.version = version;
        this.drlContent = drlContent;
        this.changeDescription = changeDescription;
        this.createdBy = createdBy;
        this.createdAt = Instant.now();
    }

    // Getters and Setters
    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }

    public UUID getRuleId() { return ruleId; }
    public void setRuleId(UUID ruleId) { this.ruleId = ruleId; }

    public Integer getVersion() { return version; }
    public void setVersion(Integer version) { this.version = version; }

    public String getDrlContent() { return drlContent; }
    public void setDrlContent(String drlContent) { this.drlContent = drlContent; }

    public String getChangeDescription() { return changeDescription; }
    public void setChangeDescription(String changeDescription) { this.changeDescription = changeDescription; }

    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }

    public String getCreatedBy() { return createdBy; }
    public void setCreatedBy(String createdBy) { this.createdBy = createdBy; }

    @Override
    public String toString() {
        return "RuleVersion{" +
                "id=" + id +
                ", ruleId=" + ruleId +
                ", version=" + version +
                ", changeDescription='" + changeDescription + '\'' +
                ", createdBy='" + createdBy + '\'' +
                ", createdAt=" + createdAt +
                '}';
    }
}
