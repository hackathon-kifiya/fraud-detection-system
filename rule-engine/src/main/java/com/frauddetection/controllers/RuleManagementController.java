package com.frauddetection.controllers;

import com.frauddetection.domain.Rule;
import com.frauddetection.dto.RuleRequestDto;
import com.frauddetection.dto.RuleResponseDto;
import com.frauddetection.mapper.RuleMapper;
import com.frauddetection.services.RuleManagementService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.Data;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/rules")
@Tag(name = "Rule Management", description = "Create, manage, validate, and deploy fraud detection rules")
public class RuleManagementController {

    @Autowired
    private RuleManagementService ruleManagementService;

    @Autowired
    private RuleMapper ruleMapper;

    @Operation(
        summary = "Create a new rule",
        description = "Creates a new rule with DRL content. The rule must be validated before creation."
    )
    @PostMapping
    public ResponseEntity<RuleResponseDto> createRule(@RequestBody RuleRequestDto request) {
        Rule rule = ruleManagementService.createRule(request);
        RuleResponseDto response = ruleMapper.toDto(rule);
        return ResponseEntity.ok(response);
    }

    @Operation(
        summary = "Get all rules",
        description = "Retrieves all rules with optional filtering by data type, status, and search term. Supports pagination."
    )
    @GetMapping
    public ResponseEntity<Map<String, Object>> getAllRules(
            @RequestParam(value = "dataType", required = false) String dataType,
            @RequestParam(value = "status", required = false) String status,
            @RequestParam(value = "search", required = false) String search,
            @RequestParam(value = "limit", required = false) Integer limit,
            @RequestParam(value = "offset", required = false) Integer offset) {

        Page<Rule> rules = ruleManagementService.searchRulesWithPagination(search, dataType, status, limit, offset);
        List<RuleResponseDto> dtoList = rules.getContent().stream()
                .map(ruleMapper::toDto)
                .collect(Collectors.toList());
        
        // Return a simple map instead of Page to avoid serialization issues
        Map<String, Object> response = new HashMap<>();
        response.put("content", dtoList);
        response.put("totalElements", rules.getTotalElements());
        response.put("number", rules.getNumber());
        response.put("size", rules.getSize());
        
        return ResponseEntity.ok(response);
    }

    @Operation(
        summary = "Get loan rule template",
        description = "Returns a template DRL for creating loan rules with necessary declarations and commented examples."
    )
    @GetMapping("/templates/loan")
    public ResponseEntity<Map<String, String>> getLoanRuleTemplate() {
        String template = "package rules;\n" +
                "import com.frauddetection.domain.DynamicFact;\n\n" +
                "// Example: Multiple loan defaults\n" +
                "//rule \"MultipleDefaultsAlert\"\n" +
                "//when\n" +
                "//    $fact : DynamicFact( getPropertyAsNumber(\"defaults_count\").doubleValue() > 2 )\n" +
                "//then\n" +
                "//    $fact.addViolation(\"MULTIPLE_DEFAULTS\", \"Customer has multiple loan defaults\", 10);\n" +
                "//end\n";
        
        Map<String, String> response = new HashMap<>();
        response.put("drlContent", template);
        return ResponseEntity.ok(response);
    }

    @Operation(
        summary = "Get rule template",
        description = "Returns a template DRL for creating rules"
    )
    @GetMapping("/template")
    public ResponseEntity<String> getTemplate() {
        
        String template = "package rules;\n" +
                        "import com.frauddetection.domain.DynamicFact;\n\n" +
                        "rule \"High Amount Transaction\"\n" +
                        "//when\n" +
                        "//    $f: DynamicFact(\n" +
                        "//        dataType == \"transaction\",\n" +
                        "//        getDoubleProperty(\"amount\") > 10000\n" +
                        "//    )\n" +
                        "//then\n" +
                        "//    $f.addViolation(\"TXN_HIGH_AMOUNT\", 20, \"Transaction amount exceeds threshold\");\n" +
                        "//end";
        return ResponseEntity.ok(template);
    }

    @Operation(summary = "Get rule by ID")
    @GetMapping("/{id}")
    public ResponseEntity<RuleResponseDto> getRule(
            @Parameter(description = "Rule UUID") @PathVariable("id") UUID id) {
        RuleResponseDto rule = ruleManagementService.getRuleById(id);
        return ResponseEntity.ok(rule);
    }

    @Operation(summary = "Update a rule", description = "Updates an existing rule. Creates a new version for change tracking.")
    @PutMapping("/{id}")
    public ResponseEntity<RuleResponseDto> updateRule(
            @Parameter(description = "Rule UUID") @PathVariable("id") UUID id,
            @RequestBody RuleRequestDto request) {
        Rule rule = ruleManagementService.updateRule(id, request, request.getUpdatedBy());
        RuleResponseDto response = ruleMapper.toDto(rule);
        return ResponseEntity.ok(response);
    }

    @Operation(summary = "Delete a rule", description = "Soft deletes a rule (marks as deleted)")
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteRule(@Parameter(description = "Rule UUID") @PathVariable("id") UUID id) {
        ruleManagementService.deleteRule(id);
        return ResponseEntity.noContent().build();
    }

    @Operation(summary = "Activate a rule", description = "Activates a rule to make it active for evaluation")
    @PostMapping("/{id}/activate")
    public ResponseEntity<RuleResponseDto> activateRule(@Parameter(description = "Rule UUID") @PathVariable("id") UUID id) {
        Rule rule = ruleManagementService.activateRule(id);
        RuleResponseDto response = ruleMapper.toDto(rule);
        return ResponseEntity.ok(response);
    }

    @Operation(summary = "Deactivate a rule", description = "Deactivates a rule (does not delete it)")
    @PostMapping("/{id}/deactivate")
    public ResponseEntity<RuleResponseDto> deactivateRule(@Parameter(description = "Rule UUID") @PathVariable("id") UUID id) {
        Rule rule = ruleManagementService.deactivateRule(id);
        RuleResponseDto response = ruleMapper.toDto(rule);
        return ResponseEntity.ok(response);
    }

    @Operation(
        summary = "Validate DRL syntax",
        description = "Validates Drools Rule Language (DRL) syntax and semantics before creating or updating a rule. Returns validation results with any errors."
    )
    @PostMapping("/validate")
    public ResponseEntity<Map<String, Object>> validateDrl(@RequestBody ValidateDrlRequest request) {
        Map<String, Object> response = ruleManagementService.validateDrlContent(request.drlContent, request.dataType);
        return ResponseEntity.ok(response);
    }

    @Data
    public static class ValidateDrlRequest {
        private String drlContent;
        private String dataType;
    }

}
