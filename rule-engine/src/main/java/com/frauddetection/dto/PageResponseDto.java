package com.frauddetection.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class PageResponseDto<T> {
    private List<T> content;
    private long totalElements;
    private int number;
    private int size;
    private int totalPages;
    private boolean first;
    private boolean last;
}

