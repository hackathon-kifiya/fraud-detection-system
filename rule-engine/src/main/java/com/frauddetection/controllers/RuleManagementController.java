package com.frauddetection.controllers;

import com.frauddetection.domain.Rule;
import com.frauddetection.domain.RuleVersion;
import com.frauddetection.services.RuleManagementService;
import com.frauddetection.services.RuleValidationService;
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
    public ResponseEntity<Map<String, Object>> createRule(@RequestBody CreateRuleRequest request) {
        try {
            Rule rule = ruleManagementService.createRule(
                request.getName(),
                request.getDataType(),
                request.getDrlContent(),
                request.getCreatedBy()
            );

            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Rule created successfully");
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

    @GetMapping
    public ResponseEntity<Map<String, Object>> getAllRules(
            @RequestParam(required = false) String dataType,
            @RequestParam(required = false) String status) {
        
        List<Rule> rules;
        
        if (dataType != null && status != null) {
            rules = ruleManagementService.getRulesByDataTypeAndStatus(
                Rule.DataType.valueOf(dataType.toUpperCase()),
                Rule.Status.valueOf(status.toUpperCase())
            );
        } else if (dataType != null) {
            rules = ruleManagementService.getRulesByDataType(Rule.DataType.valueOf(dataType.toUpperCase()));
        } else if (status != null) {
            rules = ruleManagementService.getRulesByStatus(Rule.Status.valueOf(status.toUpperCase()));
        } else {
            rules = ruleManagementService.getAllRules();
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
            Rule rule = ruleManagementService.updateRule(
                id,
                request.getDrlContent(),
                request.getChangeDescription(),
                request.getUpdatedBy()
            );

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

    // Request DTOs
    public static class CreateRuleRequest {
        private String name;
        private Rule.DataType dataType;
        private String drlContent;
        private String createdBy;

        // Getters and Setters
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public Rule.DataType getDataType() { return dataType; }
        public void setDataType(Rule.DataType dataType) { this.dataType = dataType; }
        public String getDrlContent() { return drlContent; }
        public void setDrlContent(String drlContent) { this.drlContent = drlContent; }
        public String getCreatedBy() { return createdBy; }
        public void setCreatedBy(String createdBy) { this.createdBy = createdBy; }
    }

    public static class UpdateRuleRequest {
        private String drlContent;
        private String changeDescription;
        private String updatedBy;

        // Getters and Setters
        public String getDrlContent() { return drlContent; }
        public void setDrlContent(String drlContent) { this.drlContent = drlContent; }
        public String getChangeDescription() { return changeDescription; }
        public void setChangeDescription(String changeDescription) { this.changeDescription = changeDescription; }
        public String getUpdatedBy() { return updatedBy; }
        public void setUpdatedBy(String updatedBy) { this.updatedBy = updatedBy; }
    }

    public static class ValidateDrlRequest {
        private String drlContent;
        private Rule.DataType dataType;

        // Getters and Setters
        public String getDrlContent() { return drlContent; }
        public void setDrlContent(String drlContent) { this.drlContent = drlContent; }
        public Rule.DataType getDataType() { return dataType; }
        public void setDataType(Rule.DataType dataType) { this.dataType = dataType; }
    }

    public static class RollbackRequest {
        private String rolledBackBy;

        // Getters and Setters
        public String getRolledBackBy() { return rolledBackBy; }
        public void setRolledBackBy(String rolledBackBy) { this.rolledBackBy = rolledBackBy; }
    }
}
