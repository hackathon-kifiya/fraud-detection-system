package com.frauddetection.mapper;

import com.frauddetection.domain.Evaluation;
import com.frauddetection.dto.EvaluationResponseDto;
import org.mapstruct.Mapper;
import org.mapstruct.AfterMapping;
import org.mapstruct.MappingTarget;

@Mapper(componentModel = "spring")
public interface EvaluateMapper {

    EvaluationResponseDto toDto(Evaluation entity);
    
    @AfterMapping
    default void setViolationsCount(@MappingTarget EvaluationResponseDto dto, Evaluation evaluation) {
        int count = evaluation.getViolations() != null ? evaluation.getViolations().size() : 0;
        dto.setViolationsCount(count);
    }
}
