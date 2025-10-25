package com.frauddetection.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.*;

import java.util.List;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class EvaluationResponseDto {

    private String entityId;
    private Double riskScore;
    private Integer violationsCount;
    private List<ViolationDto> violations;
    private EvaluationResponseMetadataDto metadata;

}
