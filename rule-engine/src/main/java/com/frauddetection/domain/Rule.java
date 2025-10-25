package com.frauddetection.domain;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;

import java.time.Instant;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@SuperBuilder
public class Rule {
    private UUID id;
    private String name;
    private String description;
    private String dataType;
    private String drlContent;
    private Status status;
    private Instant createdAt;
    private Instant updatedAt;
    private String createdBy;
    private String updatedBy;

    public enum Status {
        ACTIVE, INACTIVE, DRAFT
    }
}
