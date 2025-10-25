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
    public Rule createRule(String name, String description, String dataType, String drlContent, String createdBy) {
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
        Rule rule = new Rule(name, description, dataType, drlContent, createdBy);
        rule = ruleRepository.save(rule);

        // Create initial version
        RuleVersion version = new RuleVersion(rule.getId(), 1, drlContent, "Initial version", createdBy);
        ruleVersionRepository.save(version);

        return rule;
    }

    @Transactional
    public Rule updateRule(UUID ruleId, String name, String description, String dataType, String drlContent, String changeDescription, String updatedBy) {
        Rule rule = ruleRepository.findById(ruleId)
                .orElseThrow(() -> new IllegalArgumentException("Rule not found with id: " + ruleId));

        // Check if name is being changed and if new name already exists
        if (!rule.getName().equals(name) && ruleRepository.findByName(name).isPresent()) {
            throw new IllegalArgumentException("Rule with name '" + name + "' already exists");
        }

        // Validate DRL content
        RuleValidationService.ValidationResult validation = validationService.validateDrl(drlContent, dataType);
        if (!validation.isValid()) {
            throw new IllegalArgumentException("DRL validation failed: " + String.join(", ", validation.getErrors()));
        }

        // Create new version
        int newVersion = rule.getVersion() + 1;
        RuleVersion version = new RuleVersion(ruleId, newVersion, drlContent, changeDescription, updatedBy);
        ruleVersionRepository.save(version);

        // Update rule
        rule.setName(name);
        rule.setDescription(description);
        rule.setDataType(dataType);
        rule.setDrlContent(drlContent);
        rule.setVersion(newVersion);
        rule.setUpdatedAt(Instant.now());
        rule.setUpdatedBy(updatedBy);
        rule = ruleRepository.save(rule);

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
        rule.setUpdatedBy(updatedBy);
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

    public List<Rule> getRulesByDataType(String dataType) {
        return ruleRepository.findByDataType(dataType);
    }

    public List<Rule> getRulesByDataTypeAndStatus(String dataType, Rule.Status status) {
        return ruleRepository.findByDataTypeAndStatus(dataType, status);
    }

    public List<Rule> getActiveRulesByDataType(String dataType) {
        return ruleRepository.findActiveRulesByDataType(dataType);
    }

    public List<Rule> getRulesByStatus(Rule.Status status) {
        return ruleRepository.findByStatus(status);
    }

    public List<Rule> searchRules(String search, String dataType, String status, Integer limit, Integer offset) {
        // Handle search with filters
        if (search != null && !search.trim().isEmpty()) {
            if (dataType != null && status != null) {
                return ruleRepository.findByNameOrDescriptionContainingIgnoreCaseAndDataTypeAndStatus(
                    "%" + search + "%", dataType, status);
            } else if (dataType != null) {
                return ruleRepository.findByNameOrDescriptionContainingIgnoreCaseAndDataType(
                    "%" + search + "%", dataType);
            } else if (status != null) {
                return ruleRepository.findByNameOrDescriptionContainingIgnoreCaseAndStatus(
                    "%" + search + "%", status);
            } else {
                return ruleRepository.findByNameOrDescriptionContainingIgnoreCase("%" + search + "%");
            }
        }
        
        // Handle filters without search
        if (dataType != null && status != null) {
            return ruleRepository.findByDataTypeAndStatus(dataType, Rule.Status.valueOf(status.toUpperCase()));
        } else if (dataType != null) {
            return ruleRepository.findByDataType(dataType);
        } else if (status != null) {
            return ruleRepository.findByStatus(Rule.Status.valueOf(status.toUpperCase()));
        } else {
            return ruleRepository.findAllOrderByCreatedAt();
        }
    }

    public List<Rule> searchRulesWithPagination(String search, String dataType, String status, Integer limit, Integer offset) {
        // Set default values
        int limitValue = limit != null ? limit : 100;
        int offsetValue = offset != null ? offset : 0;
        
        // Handle search with filters
        if (search != null && !search.trim().isEmpty()) {
            if (dataType != null && status != null) {
                return ruleRepository.findByNameOrDescriptionContainingIgnoreCaseAndDataTypeAndStatusWithPagination(
                    "%" + search + "%", dataType, status, limitValue, offsetValue);
            } else if (dataType != null) {
                return ruleRepository.findByNameOrDescriptionContainingIgnoreCaseAndDataTypeWithPagination(
                    "%" + search + "%", dataType, limitValue, offsetValue);
            } else if (status != null) {
                return ruleRepository.findByNameOrDescriptionContainingIgnoreCaseAndStatusWithPagination(
                    "%" + search + "%", status, limitValue, offsetValue);
            } else {
                return ruleRepository.findByNameOrDescriptionContainingIgnoreCaseWithPagination(
                    "%" + search + "%", limitValue, offsetValue);
            }
        }
        
        // Handle filters without search
        if (dataType != null && status != null) {
            return ruleRepository.findByDataTypeAndStatusWithPagination(dataType, status, limitValue, offsetValue);
        } else if (dataType != null) {
            return ruleRepository.findByDataTypeWithPagination(dataType, limitValue, offsetValue);
        } else if (status != null) {
            return ruleRepository.findByStatusWithPagination(status, limitValue, offsetValue);
        } else {
            return ruleRepository.findAllOrderByCreatedAtWithPagination(limitValue, offsetValue);
        }
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

    public RuleValidationService.ValidationResult validateDrl(String drlContent, String dataType) {
        return validationService.validateDrl(drlContent, dataType);
    }
}
