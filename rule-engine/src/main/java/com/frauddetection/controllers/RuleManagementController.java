package com.frauddetection.controllers;

import com.frauddetection.domain.Rule;
import com.frauddetection.dto.RuleRequestDto;
import com.frauddetection.dto.RuleResponseDto;
import com.frauddetection.services.RuleManagementService;
import lombok.Data;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

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
    public ResponseEntity<Page<RuleResponseDto>> getAllRules(
            @RequestParam(value = "dataType", required = false) String dataType,
            @RequestParam(value = "status", required = false) String status,
            @RequestParam(value = "search", required = false) String search,
            @RequestParam(value = "limit", required = false) Integer limit,
            @RequestParam(value = "offset", required = false) Integer offset) {

        Page<Rule> rules = ruleManagementService.searchRulesWithPagination(search, dataType, status, limit, offset);
        return ResponseEntity.ok(rules);
    }

    @GetMapping("/{id}")
    public Optional<RuleResponseDto> getRule(@PathVariable UUID id) {
        return ruleManagementService.getRuleById(id);
    }

    @PutMapping("/{id}")
    public ResponseEntity<RuleResponseDto> updateRule(
            @PathVariable UUID id,
            @RequestBody RuleRequestDto request) {
        RuleResponseDto responseDto = RuleResponseDto.builder().build();
        return ResponseEntity.ok(responseDto);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> deleteRule(@PathVariable UUID id) {
        ruleManagementService.deleteRule(id);
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "Rule deactivated successfully");
        return ResponseEntity.ok(response);
    }

    @PostMapping("/{id}/activate")
    public ResponseEntity<Map<String, Object>> activateRule(@PathVariable UUID id) {
        Rule rule = ruleManagementService.activateRule(id);
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "Rule activated successfully");
        response.put("rule", rule);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/{id}/deactivate")
    public ResponseEntity<Map<String, Object>> deactivateRule(@PathVariable UUID id) {
            Rule rule = ruleManagementService.deactivateRule(id);
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Rule deactivated successfully");
            response.put("rule", rule);
            return ResponseEntity.ok(response);
    }

    @Data
    public static class ValidateDrlRequest {
        private String drlContent;
        private String dataType;
    }

}
