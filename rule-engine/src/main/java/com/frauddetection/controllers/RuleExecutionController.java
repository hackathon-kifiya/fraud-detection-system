package com.frauddetection.controllers;

import com.frauddetection.domain.EvaluationRequest;
import com.frauddetection.domain.EvaluationResponse;
import com.frauddetection.domain.Violation;
import com.frauddetection.services.DynamicRuleExecutionService;
import lombok.Data;
import lombok.EqualsAndHashCode;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/evaluate")
public class RuleExecutionController {

    @Autowired
    private DynamicRuleExecutionService executionService;

    @PostMapping("/transaction")
    public ResponseEntity<EvaluationResultResponse> evaluateTransaction(@RequestBody TransactionEvaluationRequest request) {
        try {
            EvaluationRequest evalRequest = new EvaluationRequest(
                EvaluationRequest.DataType.TRANSACTION,
                request.getFacts()
            );
            
            EvaluationResponse response = executionService.evaluateFacts(evalRequest);
            return ResponseEntity.ok(EvaluationResultResponse.success(response));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(EvaluationResultResponse.error("Evaluation failed: " + e.getMessage()));
        }
    }

    @PostMapping("/kyc")
    public ResponseEntity<EvaluationResultResponse> evaluateKyc(@RequestBody KycEvaluationRequest request) {
        try {
            EvaluationRequest evalRequest = new EvaluationRequest(
                EvaluationRequest.DataType.KYC,
                request.getFacts()
            );
            
            EvaluationResponse response = executionService.evaluateFacts(evalRequest);
            return ResponseEntity.ok(EvaluationResultResponse.success(response));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(EvaluationResultResponse.error("Evaluation failed: " + e.getMessage()));
        }
    }

    @PostMapping("/loan")
    public ResponseEntity<EvaluationResultResponse> evaluateLoan(@RequestBody LoanEvaluationRequest request) {
        try {
            EvaluationRequest evalRequest = new EvaluationRequest(
                EvaluationRequest.DataType.LOAN,
                request.getFacts()
            );
            
            EvaluationResponse response = executionService.evaluateFacts(evalRequest);
            return ResponseEntity.ok(EvaluationResultResponse.success(response));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(EvaluationResultResponse.error("Evaluation failed: " + e.getMessage()));
        }
    }

    @PostMapping("/credit")
    public ResponseEntity<EvaluationResultResponse> evaluateCredit(@RequestBody CreditEvaluationRequest request) {
        try {
            EvaluationRequest evalRequest = new EvaluationRequest(
                EvaluationRequest.DataType.CREDIT,
                request.getFacts()
            );
            
            EvaluationResponse response = executionService.evaluateFacts(evalRequest);
            return ResponseEntity.ok(EvaluationResultResponse.success(response));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(EvaluationResultResponse.error("Evaluation failed: " + e.getMessage()));
        }
    }

    @PostMapping("/repayment")
    public ResponseEntity<EvaluationResultResponse> evaluateRepayment(@RequestBody RepaymentEvaluationRequest request) {
        try {
            EvaluationRequest evalRequest = new EvaluationRequest(
                EvaluationRequest.DataType.REPAYMENT,
                request.getFacts()
            );
            
            EvaluationResponse response = executionService.evaluateFacts(evalRequest);
            return ResponseEntity.ok(EvaluationResultResponse.success(response));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(EvaluationResultResponse.error("Evaluation failed: " + e.getMessage()));
        }
    }

    @PostMapping("/generic")
    public ResponseEntity<EvaluationResultResponse> evaluateGeneric(@RequestBody GenericEvaluationRequest request) {
        try {
            EvaluationResponse response = executionService.evaluateFacts(request);
            return ResponseEntity.ok(EvaluationResultResponse.success(response));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(EvaluationResultResponse.error("Evaluation failed: " + e.getMessage()));
        }
    }

    // Request DTOs for different data types
    @Data
    public static class TransactionEvaluationRequest {
        private List<Map<String, Object>> facts;
    }

    @Data
    public static class KycEvaluationRequest {
        private List<Map<String, Object>> facts;
    }

    @Data
    public static class LoanEvaluationRequest {
        private List<Map<String, Object>> facts;
    }

    @Data
    public static class CreditEvaluationRequest {
        private List<Map<String, Object>> facts;
    }

    @Data
    public static class RepaymentEvaluationRequest {
        private List<Map<String, Object>> facts;
    }

    @Data
    @EqualsAndHashCode(callSuper = false)
    public static class GenericEvaluationRequest extends EvaluationRequest {
        public GenericEvaluationRequest() {
            super(null, null);
        }
    }

    // Response DTOs
    @Data
    public static class EvaluationResultResponse {
        private boolean success;
        private double riskScore;
        private EvaluationResponse.Verdict verdict;
        private List<Violation> violations;
        private String entityId;
        private Map<String, Object> metadata;
        private String error;

        public static EvaluationResultResponse success(EvaluationResponse response) {
            EvaluationResultResponse result = new EvaluationResultResponse();
            result.setSuccess(true);
            result.setRiskScore(response.getRiskScore());
            result.setVerdict(response.getVerdict());
            result.setViolations(response.getViolations());
            result.setEntityId(response.getEntityId());
            result.setMetadata(response.getMetadata());
            return result;
        }

        public static EvaluationResultResponse error(String errorMessage) {
            EvaluationResultResponse result = new EvaluationResultResponse();
            result.setSuccess(false);
            result.setError(errorMessage);
            return result;
        }
    }
}
