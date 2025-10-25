package com.frauddetection.controllers;

import com.frauddetection.domain.EvaluationRequest;
import com.frauddetection.domain.EvaluationResponse;
import com.frauddetection.services.DynamicRuleExecutionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class RuleExecutionController {

    @Autowired
    private DynamicRuleExecutionService executionService;

    @PostMapping("/evaluate")
    public ResponseEntity<Map<String, Object>> evaluate(@RequestBody EvaluationRequest request) {
        try {
            EvaluationResponse response = executionService.evaluateFacts(request);
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("response", response);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            Map<String, Object> result = new HashMap<>();
            result.put("success", false);
            result.put("error", "Evaluation failed: " + e.getMessage());
            return ResponseEntity.badRequest().body(result);
        }
    }

}
