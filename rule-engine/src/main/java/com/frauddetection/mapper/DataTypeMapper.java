package com.frauddetection.mapper;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.frauddetection.domain.DataType;
import com.frauddetection.dto.DataTypeRequestDto;
import com.frauddetection.dto.DataTypeResponseDto;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;
import org.mapstruct.Named;

import java.util.Map;

@Mapper(componentModel = "spring")
public interface DataTypeMapper {
    
    @Mapping(target = "schemaDefinition", source = "schemaDefinition", qualifiedByName = "stringToMap")
    @Mapping(target = "sampleData", source = "sampleData", qualifiedByName = "stringToMap")
    @Mapping(target = "status", source = "status", qualifiedByName = "statusToString")
    DataTypeResponseDto toDto(DataType entity);
    
    /**
     * Maps DataType entity to DTO with schema definition and sample data parsed.
     */
    default DataTypeResponseDto toDtoWithSchema(DataType entity) {
        return toDto(entity); // Already handles the conversion
    }
    
    @Mapping(target = "schemaDefinition", source = "schemaDefinition", qualifiedByName = "mapToString")
    @Mapping(target = "sampleData", source = "sampleData", qualifiedByName = "mapToString")
    @Mapping(target = "status", ignore = true)
    @Mapping(target = "id", ignore = true)
    DataType toEntity(DataTypeRequestDto dto);
    
    @Named("statusToString")
    default String statusToString(DataType.Status status) {
        return status != null ? status.name() : null;
    }
    
    @Named("stringToStatus")
    default DataType.Status stringToStatus(String status) {
        return status != null ? DataType.Status.valueOf(status.toUpperCase()) : null;
    }
    
    @Named("mapToString")
    default String mapToString(Map<String, Object> map) {
        if (map == null) {
            return null;
        }
        try {
            ObjectMapper mapper = new ObjectMapper();
            return mapper.writeValueAsString(map);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to serialize map", e);
        }
    }
    
    @Named("stringToMap")
    default Map<String, Object> stringToMap(String json) {
        if (json == null || json.trim().isEmpty()) {
            return null;
        }
        try {
            ObjectMapper mapper = new ObjectMapper();
            return mapper.readValue(json, new TypeReference<Map<String, Object>>() {});
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to deserialize JSON", e);
        }
    }
}

