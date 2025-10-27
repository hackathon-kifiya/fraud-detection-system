package com.frauddetection.mapper;

import com.frauddetection.domain.Rule;
import com.frauddetection.dto.RuleRequestDto;
import com.frauddetection.dto.RuleResponseDto;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.Named;

@Mapper(componentModel = "spring")
public interface RuleMapper {

    @Mapping(target = "id", ignore = true)
    Rule toEntity(RuleRequestDto entity);

    @Mapping(target = "status", source = "status", qualifiedByName = "statusToString")
    RuleResponseDto toDto(Rule entity);

    @Named("statusToString")
    default String statusToString(Rule.Status status) {
        return status != null ? status.name() : null;
    }
}
