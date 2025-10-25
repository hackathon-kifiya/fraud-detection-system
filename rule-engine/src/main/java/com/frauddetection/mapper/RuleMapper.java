package com.frauddetection.mapper;

import com.frauddetection.domain.EvaluationQuery;
import com.frauddetection.dto.EvaluationQueryRequestDto;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface RuleMapper {

    EvaluationQuery toEntity(RuleE entity);
}
