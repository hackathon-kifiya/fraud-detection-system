package com.frauddetection.domain;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RuleVersion {
    private UUID id;
    private UUID ruleId;
    private Integer version;
    private String drlContent;
    private String changeDescription;
    private Instant createdAt;
    private String createdBy;
}
