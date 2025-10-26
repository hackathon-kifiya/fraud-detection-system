package com.frauddetection.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class RuleRequestDto {
    private String name;
    private String description;
    private String dataType;
    private String drlContent;
    private String createdBy;
    private String updatedBy;
}

