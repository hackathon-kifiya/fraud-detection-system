package com.frauddetection.mapper;

import com.frauddetection.domain.EvaluationQuery;
import com.frauddetection.domain.Rule;
import com.frauddetection.dto.EvaluationQueryRequestDto;
import com.frauddetection.dto.RuleRequestDto;
import com.frauddetection.dto.RuleResponseDto;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface RuleMapper {

    Rule toEntity(RuleRequestDto entity);

    RuleResponseDto toDto(Rule entity);
}
