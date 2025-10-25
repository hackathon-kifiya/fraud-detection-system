package com.frauddetection.mapper;

import com.frauddetection.domain.Evaluation;
import com.frauddetection.dto.EvaluationResponseDto;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface EvaluateMapper {

    EvaluationResponseDto toDto(Evaluation entity);
}
