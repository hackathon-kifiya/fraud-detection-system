package com.frauddetection.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
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
    @NotBlank(message = "Rule name is required")
    private String name;
    
    private String description;
    
    @NotBlank(message = "Data type is required")
    @NotNull(message = "Data type is required")
    private String dataType;
    
    @NotBlank(message = "DRL content is required")
    private String drlContent;
    
    private String createdBy;
    private String updatedBy;
}

