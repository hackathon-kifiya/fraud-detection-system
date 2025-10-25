package com.frauddetection.mapper;

import com.frauddetection.domain.Rule;
import com.frauddetection.dto.RuleRequestDto;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface RuleMapper {

    default Rule toEntity(RuleRequestDto entity) {
        return null;
    }
}
