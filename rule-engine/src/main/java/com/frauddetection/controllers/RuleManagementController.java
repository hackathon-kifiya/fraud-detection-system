package com.frauddetection.controllers;

import com.frauddetection.domain.Rule;
import com.frauddetection.domain.RuleVersion;
import com.frauddetection.dto.RuleRequestDto;
import com.frauddetection.mapper.RuleMapper;
import com.frauddetection.services.RuleManagementService;
import com.frauddetection.services.RuleValidationService;
import lombok.Data;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/rules")
public class RuleManagementController {

    @Autowired
    private RuleManagementService ruleManagementService;

    @PostMapping
    public ResponseEntity<Map<String, Object>> createRule(@RequestBody RuleRequestDto request) {
        Rule rule = ruleManagementService.createRule(request);

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "Rule created successfully");
        response.put("rule", rule);
        return ResponseEntity.ok(response);
    }

    @GetMapping
    public ResponseEntity<Map<String, Object>> getAllRules(
            @RequestParam(value = "dataType", required = false) String dataType,
            @RequestParam(value = "status", required = false) String status,
            @RequestParam(value = "search", required = false) String search,
            @RequestParam(value = "limit", required = false) Integer limit,
            @RequestParam(value = "offset", required = false) Integer offset) {
        
        List<Rule> rules;
        
        // Use pagination if limit is provided
        if (limit != null) {
            rules = ruleManagementService.searchRulesWithPagination(search, dataType, status, limit, offset);
        } else {
            rules = ruleManagementService.searchRules(search, dataType, status, limit, offset);
        }

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("rules", rules);
        response.put("count", rules.size());
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getRule(@PathVariable UUID id) {
        return ruleManagementService.getRuleById(id)
                .map(rule -> {
                    Map<String, Object> response = new HashMap<>();
                    response.put("success", true);
                    response.put("rule", rule);
                    return ResponseEntity.ok(response);
                })
                .orElse(ResponseEntity.notFound().build());
    }

    @PutMapping("/{id}")
    public ResponseEntity<Map<String, Object>> updateRule(
            @PathVariable UUID id,
            @RequestBody UpdateRuleRequest request) {
        try {
            Rule rule;
            
            // Check if this is a full update (with name, description, dataType) or just DRL update
            if (request.getName() != null && request.getDescription() != null && request.getDataType() != null) {
                rule = ruleManagementService.updateRule(
                    id,
                    request.getName(),
                    request.getDescription(),
                    request.getDataType(),
                    request.getDrlContent(),
                    request.getChangeDescription(),
                    request.getUpdatedBy()
                );
            } else {
                rule = ruleManagementService.updateRule(
                    id,
                    request.getDrlContent(),
                    request.getChangeDescription(),
                    request.getUpdatedBy()
                );
            }

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Rule updated successfully");
            response.put("rule", rule);
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("error", "Internal server error: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> deleteRule(@PathVariable UUID id) {
        try {
            ruleManagementService.deleteRule(id);
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Rule deactivated successfully");
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("error", "Internal server error: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }

    @PostMapping("/{id}/activate")
    public ResponseEntity<Map<String, Object>> activateRule(@PathVariable UUID id) {
        try {
            Rule rule = ruleManagementService.activateRule(id);
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Rule activated successfully");
            response.put("rule", rule);
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("error", "Internal server error: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }

    @PostMapping("/{id}/deactivate")
    public ResponseEntity<Map<String, Object>> deactivateRule(@PathVariable UUID id) {
        try {
            Rule rule = ruleManagementService.deactivateRule(id);
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Rule deactivated successfully");
            response.put("rule", rule);
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("error", "Internal server error: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }

    @PostMapping("/validate")
    public ResponseEntity<Map<String, Object>> validateDrl(@RequestBody ValidateDrlRequest request) {
        RuleValidationService.ValidationResult result = ruleManagementService.validateDrl(
            request.getDrlContent(),
            request.getDataType()
        );

        Map<String, Object> response = new HashMap<>();
        response.put("valid", result.isValid());
        response.put("errors", result.getErrors());
        response.put("warnings", result.getWarnings());
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}/versions")
    public ResponseEntity<Map<String, Object>> getRuleVersions(@PathVariable UUID id) {
        List<RuleVersion> versions = ruleManagementService.getRuleVersions(id);
        
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("versions", versions);
        response.put("count", versions.size());
        return ResponseEntity.ok(response);
    }

    @PostMapping("/{id}/rollback/{version}")
    public ResponseEntity<Map<String, Object>> rollbackToVersion(
            @PathVariable UUID id,
            @PathVariable Integer version,
            @RequestBody RollbackRequest request) {
        try {
            Rule rule = ruleManagementService.rollbackToVersion(id, version, request.getRolledBackBy());
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Rule rolled back to version " + version);
            response.put("rule", rule);
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("error", e.getMessage());
            return ResponseEntity.badRequest().body(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("success", false);
            response.put("error", "Internal server error: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }

    @Data
    public static class ValidateDrlRequest {
        private String drlContent;
        private String dataType;
    }

    @Data
    public static class RollbackRequest {
        private String rolledBackBy;
    }
}
