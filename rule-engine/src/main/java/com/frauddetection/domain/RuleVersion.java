package com.frauddetection.domain;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class RuleVersion {
    private UUID id;
    private UUID ruleId;
    private Integer version;
    private String drlContent;
    private String changeDescription;
    private Instant createdAt;
    private String createdBy;

    // Constructor for creating new versions
    public RuleVersion(UUID ruleId, Integer version, String drlContent, String changeDescription, String createdBy) {
        this.ruleId = ruleId;
        this.version = version;
        this.drlContent = drlContent;
        this.changeDescription = changeDescription;
        this.createdBy = createdBy;
        this.createdAt = Instant.now();
    }
}
