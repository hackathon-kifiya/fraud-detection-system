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
@RequestMapping("/api/evaluate")
public class RuleExecutionController {

    @Autowired
    private DynamicRuleExecutionService executionService;

    @PostMapping("/transaction")
    public ResponseEntity<Map<String, Object>> evaluateTransaction(@RequestBody TransactionEvaluationRequest request) {
        try {
            EvaluationRequest evalRequest = new EvaluationRequest(
                EvaluationRequest.DataType.TRANSACTION,
                request.getFacts()
            );
            
            EvaluationResponse response = executionService.evaluateFacts(evalRequest);
            
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

    @PostMapping("/kyc")
    public ResponseEntity<Map<String, Object>> evaluateKyc(@RequestBody KycEvaluationRequest request) {
        try {
            EvaluationRequest evalRequest = new EvaluationRequest(
                EvaluationRequest.DataType.KYC,
                request.getFacts()
            );
            
            EvaluationResponse response = executionService.evaluateFacts(evalRequest);
            
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

    @PostMapping("/loan")
    public ResponseEntity<Map<String, Object>> evaluateLoan(@RequestBody LoanEvaluationRequest request) {
        try {
            EvaluationRequest evalRequest = new EvaluationRequest(
                EvaluationRequest.DataType.LOAN,
                request.getFacts()
            );
            
            EvaluationResponse response = executionService.evaluateFacts(evalRequest);
            
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

    @PostMapping("/credit")
    public ResponseEntity<Map<String, Object>> evaluateCredit(@RequestBody CreditEvaluationRequest request) {
        try {
            EvaluationRequest evalRequest = new EvaluationRequest(
                EvaluationRequest.DataType.CREDIT,
                request.getFacts()
            );
            
            EvaluationResponse response = executionService.evaluateFacts(evalRequest);
            
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

    @PostMapping("/repayment")
    public ResponseEntity<Map<String, Object>> evaluateRepayment(@RequestBody RepaymentEvaluationRequest request) {
        try {
            EvaluationRequest evalRequest = new EvaluationRequest(
                EvaluationRequest.DataType.REPAYMENT,
                request.getFacts()
            );
            
            EvaluationResponse response = executionService.evaluateFacts(evalRequest);
            
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

    @PostMapping("/generic")
    public ResponseEntity<Map<String, Object>> evaluateGeneric(@RequestBody GenericEvaluationRequest request) {
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

    // Request DTOs for different data types
    public static class TransactionEvaluationRequest {
        private List<Map<String, Object>> facts;

        public List<Map<String, Object>> getFacts() { return facts; }
        public void setFacts(List<Map<String, Object>> facts) { this.facts = facts; }
    }

    public static class KycEvaluationRequest {
        private List<Map<String, Object>> facts;

        public List<Map<String, Object>> getFacts() { return facts; }
        public void setFacts(List<Map<String, Object>> facts) { this.facts = facts; }
    }

    public static class LoanEvaluationRequest {
        private List<Map<String, Object>> facts;

        public List<Map<String, Object>> getFacts() { return facts; }
        public void setFacts(List<Map<String, Object>> facts) { this.facts = facts; }
    }

    public static class CreditEvaluationRequest {
        private List<Map<String, Object>> facts;

        public List<Map<String, Object>> getFacts() { return facts; }
        public void setFacts(List<Map<String, Object>> facts) { this.facts = facts; }
    }

    public static class RepaymentEvaluationRequest {
        private List<Map<String, Object>> facts;

        public List<Map<String, Object>> getFacts() { return facts; }
        public void setFacts(List<Map<String, Object>> facts) { this.facts = facts; }
    }

    public static class GenericEvaluationRequest extends EvaluationRequest {
        public GenericEvaluationRequest() {
            super();
        }
    }
}
