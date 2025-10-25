package com.frauddetection.services;

import com.frauddetection.domain.Rule;
import com.frauddetection.domain.RuleVersion;
import com.frauddetection.repository.RuleRepository;
import com.frauddetection.repository.RuleVersionRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Service
public class RuleManagementService {

    @Autowired
    private RuleRepository ruleRepository;

    @Autowired
    private RuleVersionRepository ruleVersionRepository;

    @Autowired
    private RuleValidationService validationService;

    @Transactional
    public Rule createRule(String name, Rule.DataType dataType, String drlContent, String createdBy) {
        // Check if rule name already exists
        if (ruleRepository.findByName(name).isPresent()) {
            throw new IllegalArgumentException("Rule with name '" + name + "' already exists");
        }

        // Validate DRL content
        RuleValidationService.ValidationResult validation = validationService.validateDrl(drlContent, dataType);
        if (!validation.isValid()) {
            throw new IllegalArgumentException("DRL validation failed: " + String.join(", ", validation.getErrors()));
        }

        // Create new rule
        Rule rule = new Rule(name, dataType, drlContent, createdBy);
        rule = ruleRepository.save(rule);

        // Create initial version
        RuleVersion version = new RuleVersion(rule.getId(), 1, drlContent, "Initial version", createdBy);
        ruleVersionRepository.save(version);

        return rule;
    }

    @Transactional
    public Rule updateRule(UUID ruleId, String drlContent, String changeDescription, String updatedBy) {
        Rule rule = ruleRepository.findById(ruleId)
                .orElseThrow(() -> new IllegalArgumentException("Rule not found with id: " + ruleId));

        // Validate DRL content
        RuleValidationService.ValidationResult validation = validationService.validateDrl(drlContent, rule.getDataType());
        if (!validation.isValid()) {
            throw new IllegalArgumentException("DRL validation failed: " + String.join(", ", validation.getErrors()));
        }

        // Create new version
        int newVersion = rule.getVersion() + 1;
        RuleVersion version = new RuleVersion(ruleId, newVersion, drlContent, changeDescription, updatedBy);
        ruleVersionRepository.save(version);

        // Update rule
        rule.setDrlContent(drlContent);
        rule.setVersion(newVersion);
        rule.setUpdatedAt(Instant.now());
        rule = ruleRepository.save(rule);

        return rule;
    }

    @Transactional
    public void deleteRule(UUID ruleId) {
        Rule rule = ruleRepository.findById(ruleId)
                .orElseThrow(() -> new IllegalArgumentException("Rule not found with id: " + ruleId));

        // Soft delete - set status to inactive
        rule.setStatus(Rule.Status.INACTIVE);
        rule.setUpdatedAt(Instant.now());
        ruleRepository.save(rule);
    }

    @Transactional
    public Rule activateRule(UUID ruleId) {
        Rule rule = ruleRepository.findById(ruleId)
                .orElseThrow(() -> new IllegalArgumentException("Rule not found with id: " + ruleId));

        rule.setStatus(Rule.Status.ACTIVE);
        rule.setUpdatedAt(Instant.now());
        return ruleRepository.save(rule);
    }

    @Transactional
    public Rule deactivateRule(UUID ruleId) {
        Rule rule = ruleRepository.findById(ruleId)
                .orElseThrow(() -> new IllegalArgumentException("Rule not found with id: " + ruleId));

        rule.setStatus(Rule.Status.INACTIVE);
        rule.setUpdatedAt(Instant.now());
        return ruleRepository.save(rule);
    }

    public List<Rule> getAllRules() {
        return (List<Rule>) ruleRepository.findAll();
    }

    public List<Rule> getRulesByDataType(Rule.DataType dataType) {
        return ruleRepository.findByDataType(dataType);
    }

    public List<Rule> getRulesByDataTypeAndStatus(Rule.DataType dataType, Rule.Status status) {
        return ruleRepository.findByDataTypeAndStatus(dataType, status);
    }

    public List<Rule> getActiveRulesByDataType(Rule.DataType dataType) {
        return ruleRepository.findActiveRulesByDataType(dataType.name());
    }

    public List<Rule> getRulesByStatus(Rule.Status status) {
        return ruleRepository.findByStatus(status);
    }

    public Optional<Rule> getRuleById(UUID ruleId) {
        return ruleRepository.findById(ruleId);
    }

    public Optional<Rule> getRuleByName(String name) {
        return ruleRepository.findByName(name);
    }

    public List<RuleVersion> getRuleVersions(UUID ruleId) {
        return ruleVersionRepository.findByRuleIdOrderByVersionDesc(ruleId);
    }

    public Optional<RuleVersion> getRuleVersion(UUID ruleId, Integer version) {
        return ruleVersionRepository.findByRuleIdAndVersion(ruleId, version);
    }

    @Transactional
    public Rule rollbackToVersion(UUID ruleId, Integer version, String rolledBackBy) {
        Rule rule = ruleRepository.findById(ruleId)
                .orElseThrow(() -> new IllegalArgumentException("Rule not found with id: " + ruleId));

        RuleVersion targetVersion = ruleVersionRepository.findByRuleIdAndVersion(ruleId, version)
                .orElseThrow(() -> new IllegalArgumentException("Version " + version + " not found for rule " + ruleId));

        // Create new version with rolled back content
        int newVersion = rule.getVersion() + 1;
        RuleVersion rollbackVersion = new RuleVersion(ruleId, newVersion, targetVersion.getDrlContent(), 
                "Rollback to version " + version, rolledBackBy);
        ruleVersionRepository.save(rollbackVersion);

        // Update rule
        rule.setDrlContent(targetVersion.getDrlContent());
        rule.setVersion(newVersion);
        rule.setUpdatedAt(Instant.now());
        return ruleRepository.save(rule);
    }

    public RuleValidationService.ValidationResult validateDrl(String drlContent, Rule.DataType dataType) {
        return validationService.validateDrl(drlContent, dataType);
    }
}
