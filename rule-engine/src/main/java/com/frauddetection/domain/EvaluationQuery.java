package com.frauddetection.domain;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;

import java.util.List;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@SuperBuilder
public class EvaluationQuery {
    private String dataType;
    private List<Map<String, Object>> facts;
}
