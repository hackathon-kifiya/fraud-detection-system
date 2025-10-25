package com.frauddetection.domain;

import lombok.Data;

@Data
public class Violation {
    private final String code;
    private final int weight;
    private final String description;

    public Violation(String code, int weight, String description) {
        this.code = code;
        this.weight = weight;
        this.description = description;
    }
}


