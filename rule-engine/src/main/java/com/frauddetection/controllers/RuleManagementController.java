package com.frauddetection.controllers;

import com.frauddetection.domain.Rule;
import com.frauddetection.dto.PageResponseDto;
import com.frauddetection.dto.RuleRequestDto;
import com.frauddetection.dto.RuleResponseDto;
import com.frauddetection.mapper.RuleMapper;
import com.frauddetection.services.RuleManagementService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
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
    public ResponseEntity<RuleResponseDto> createRule(@Valid @RequestBody RuleRequestDto request) {
        RuleResponseDto response = ruleManagementService.createRule(request);
        return ResponseEntity.ok(response);
    }

    @Operation(
        summary = "Get all rules",
        description = "Retrieves all rules with optional filtering by data type, status, and search term. Supports pagination."
    )
    @GetMapping
    public ResponseEntity<PageResponseDto<RuleResponseDto>> getAllRules(
            @RequestParam(value = "dataType", required = false) String dataType,
            @RequestParam(value = "status", required = false) String status,
            @RequestParam(value = "search", required = false) String search,
            @RequestParam(value = "limit", required = false) Integer limit,
            @RequestParam(value = "offset", required = false) Integer offset) {

        Page<Rule> rules = ruleManagementService.searchRulesWithPagination(search, dataType, status, limit, offset);
        List<RuleResponseDto> dtoList = rules.getContent().stream()
                .map(ruleMapper::toDto)
                .collect(Collectors.toList());
        
        PageResponseDto<RuleResponseDto> response = PageResponseDto.<RuleResponseDto>builder()
                .content(dtoList)
                .totalElements(rules.getTotalElements())
                .number(rules.getNumber())
                .size(rules.getSize())
                .totalPages(rules.getTotalPages())
                .first(rules.isFirst())
                .last(rules.isLast())
                .build();
        
        return ResponseEntity.ok(response);
    }

    @Operation(
        summary = "Get template",
        description = "Returns a template DRL"
    )
    @GetMapping("/example/template")
    public ResponseEntity<Map<String, String>> getTemplate() {
        
        String template = "package rules;\n\n" +
                "import com.frauddetection.domain.DynamicFact;\n\n" +
                "rule \"Example Rule\"\n";
        
        Map<String, String> response = new HashMap<>();
        response.put("drlContent", template);
        return ResponseEntity.ok(response);
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
            @Valid @RequestBody RuleRequestDto request) {
        RuleResponseDto response = ruleManagementService.updateRule(id, request, request.getUpdatedBy());
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
        RuleResponseDto response = ruleManagementService.activateRule(id);
        return ResponseEntity.ok(response);
    }

    @Operation(summary = "Deactivate a rule", description = "Deactivates a rule (does not delete it)")
    @PostMapping("/{id}/deactivate")
    public ResponseEntity<RuleResponseDto> deactivateRule(@Parameter(description = "Rule UUID") @PathVariable("id") UUID id) {
        RuleResponseDto response = ruleManagementService.deactivateRule(id);
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
