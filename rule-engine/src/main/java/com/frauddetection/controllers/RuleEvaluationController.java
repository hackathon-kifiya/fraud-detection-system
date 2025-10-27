package com.frauddetection.controllers;

import com.frauddetection.domain.EvaluationQuery;
import com.frauddetection.dto.EvaluationQueryRequestDto;
import com.frauddetection.dto.EvaluationResponseDto;
import com.frauddetection.mapper.EvaluateMapper;
import com.frauddetection.mapper.EvaluateQueryMapper;
import com.frauddetection.services.DynamicRuleExecutionService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/evaluate")
@Tag(name = "Rule Evaluation", description = "Execute rules against transaction data to calculate risk scores")
public class RuleEvaluationController {

    @Autowired
    private DynamicRuleExecutionService executionService;

    @Autowired
    private EvaluateMapper evaluateMapper;

    @Autowired
    private EvaluateQueryMapper evaluateQueryMapper;

    @Operation(
        summary = "Evaluate data against rules",
        description = """
            Evaluates transaction data against active rules for the specified data type.
            
            Returns a risk score calculated from cumulative violation weights:
            - **Score 0**: No risk detected
            - **Score 1-3**: Low risk
            - **Score 4-6**: Medium risk
            - **Score 7-10**: High risk
            - **Score 11+**: Critical risk
            
            For multiple facts, returns the average risk score.
            """,
        responses = {
            @ApiResponse(
                responseCode = "200",
                description = "Evaluation completed successfully",
                content = @Content(schema = @Schema(implementation = EvaluationResponseDto.class))
            ),
            @ApiResponse(
                responseCode = "400",
                description = "Invalid request or data type not found"
            ),
            @ApiResponse(
                responseCode = "500",
                description = "Rule execution error"
            )
        }
    )
    @PostMapping("/")
    public ResponseEntity<EvaluationResponseDto> evaluateGeneric(@RequestBody EvaluationQueryRequestDto request) {
        EvaluationQuery evaluationRequest = evaluateQueryMapper.toEntity(request);
        EvaluationResponseDto response = evaluateMapper.toDto(executionService.evaluateFacts(evaluationRequest));
        return ResponseEntity.ok(response);
    }
}
