package com.frauddetection.domain;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;

import java.util.ArrayList;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@SuperBuilder
public class ValidationResult {
    private boolean valid = false;
    private List<String> errors = new ArrayList<>();
    private List<String> warnings = new ArrayList<>();
}
