package com.frauddetection.controllers;

import com.frauddetection.domain.EvaluationQuery;
import com.frauddetection.dto.EvaluationQueryRequestDto;
import com.frauddetection.dto.EvaluationResponseDto;
import com.frauddetection.mapper.EvaluateMapper;
import com.frauddetection.mapper.EvaluateQueryMapper;
import com.frauddetection.services.DynamicRuleExecutionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/evaluate")
public class RuleEvaluationController {

    @Autowired
    private DynamicRuleExecutionService executionService;

    @Autowired
    private EvaluateMapper evaluateMapper;

    @Autowired
    private EvaluateQueryMapper evaluateQueryMapper;

    @PostMapping("/")
    public ResponseEntity<EvaluationResponseDto> evaluateGeneric(@RequestBody EvaluationQueryRequestDto request) {
        EvaluationQuery evaluationRequest = evaluateQueryMapper.toEntity(request);
        EvaluationResponseDto response = evaluateMapper.toDto(executionService.evaluateFacts(evaluationRequest));
        return ResponseEntity.ok(response);
    }
}
