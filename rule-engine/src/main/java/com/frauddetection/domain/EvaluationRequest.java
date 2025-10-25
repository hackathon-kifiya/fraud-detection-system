package com.frauddetection.domain;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class EvaluationRequest {
    private String dataType;
    private List<Map<String, Object>> facts;

    @Override
    public String toString() {
        return "EvaluationRequest{" +
                "dataType=" + dataType +
                ", factsCount=" + (facts != null ? facts.size() : 0) +
                '}';
    }
}
