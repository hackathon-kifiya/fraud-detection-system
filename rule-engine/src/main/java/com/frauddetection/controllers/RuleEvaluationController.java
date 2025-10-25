package main.java.com.frauddetection.controllers;

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
@RequestMapping("/api/evaluate")
public class RuleEvaluationController {

    @Autowired
    private DynamicRuleExecutionService executionService;

    @PostMapping("/transaction")
    public ResponseEntity<Map<String, Object>> evaluateTransaction(@RequestBody Map<String, Object> request) {
        try {
            List<Map<String, Object>> facts = (List<Map<String, Object>>) request.get("facts");
            EvaluationRequest evaluationRequest = new EvaluationRequest("transaction", facts);
            EvaluationResponse response = executionService.evaluateFacts(evaluationRequest);
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("data", response);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            Map<String, Object> result = new HashMap<>();
            result.put("success", false);
            result.put("error", "Transaction evaluation failed: " + e.getMessage());
            return ResponseEntity.badRequest().body(result);
        }
    }

    @PostMapping("/kyc")
    public ResponseEntity<Map<String, Object>> evaluateKYC(@RequestBody Map<String, Object> request) {
        try {
            List<Map<String, Object>> facts = (List<Map<String, Object>>) request.get("facts");
            EvaluationRequest evaluationRequest = new EvaluationRequest("kyc", facts);
            EvaluationResponse response = executionService.evaluateFacts(evaluationRequest);
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("data", response);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            Map<String, Object> result = new HashMap<>();
            result.put("success", false);
            result.put("error", "KYC evaluation failed: " + e.getMessage());
            return ResponseEntity.badRequest().body(result);
        }
    }

    @PostMapping("/loan")
    public ResponseEntity<Map<String, Object>> evaluateLoan(@RequestBody Map<String, Object> request) {
        try {
            List<Map<String, Object>> facts = (List<Map<String, Object>>) request.get("facts");
            EvaluationRequest evaluationRequest = new EvaluationRequest("loan", facts);
            EvaluationResponse response = executionService.evaluateFacts(evaluationRequest);
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("data", response);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            Map<String, Object> result = new HashMap<>();
            result.put("success", false);
            result.put("error", "Loan evaluation failed: " + e.getMessage());
            return ResponseEntity.badRequest().body(result);
        }
    }

    @PostMapping("/credit")
    public ResponseEntity<Map<String, Object>> evaluateCredit(@RequestBody Map<String, Object> request) {
        try {
            List<Map<String, Object>> facts = (List<Map<String, Object>>) request.get("facts");
            EvaluationRequest evaluationRequest = new EvaluationRequest("credit", facts);
            EvaluationResponse response = executionService.evaluateFacts(evaluationRequest);
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("data", response);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            Map<String, Object> result = new HashMap<>();
            result.put("success", false);
            result.put("error", "Credit evaluation failed: " + e.getMessage());
            return ResponseEntity.badRequest().body(result);
        }
    }

    @PostMapping("/repayment")
    public ResponseEntity<Map<String, Object>> evaluateRepayment(@RequestBody Map<String, Object> request) {
        try {
            List<Map<String, Object>> facts = (List<Map<String, Object>>) request.get("facts");
            EvaluationRequest evaluationRequest = new EvaluationRequest("repayment", facts);
            EvaluationResponse response = executionService.evaluateFacts(evaluationRequest);
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("data", response);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            Map<String, Object> result = new HashMap<>();
            result.put("success", false);
            result.put("error", "Repayment evaluation failed: " + e.getMessage());
            return ResponseEntity.badRequest().body(result);
        }
    }

    @PostMapping("/generic")
    public ResponseEntity<Map<String, Object>> evaluateGeneric(@RequestBody Map<String, Object> request) {
        try {
            String dataType = (String) request.get("dataType");
            List<Map<String, Object>> facts = (List<Map<String, Object>>) request.get("facts");
            EvaluationRequest evaluationRequest = new EvaluationRequest(dataType, facts);
            EvaluationResponse response = executionService.evaluateFacts(evaluationRequest);
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("data", response);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            Map<String, Object> result = new HashMap<>();
            result.put("success", false);
            result.put("error", "Generic evaluation failed: " + e.getMessage());
            return ResponseEntity.badRequest().body(result);
        }
    }
}
