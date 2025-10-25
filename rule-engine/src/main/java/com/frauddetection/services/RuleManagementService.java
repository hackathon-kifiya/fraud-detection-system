package com.frauddetection.services;

import com.frauddetection.domain.Rule;
import com.frauddetection.domain.ValidationResult;
import com.frauddetection.dto.RuleRequestDto;
import com.frauddetection.dto.RuleResponseDto;
import com.frauddetection.mapper.RuleMapper;
import com.frauddetection.repository.RuleRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
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
    private RuleValidationService validationService;

    @Autowired
    private RuleMapper ruleMapper;

    public Optional<RuleResponseDto> getRuleById(UUID id) {
        return Optional.ofNullable(ruleMapper.toDto(ruleRepository.findById(id).get()));
    }

    @Transactional
    public Rule createRule(RuleRequestDto request) {
        ValidationResult validation = validationService.validateDrl(request.getDrlContent(), request.getDataType());
        if (!validation.isValid()) {
            throw new IllegalArgumentException("DRL validation failed: " + String.join(", ", validation.getErrors()));
        }

        Rule rule = ruleMapper.toEntity(request);
        rule = ruleRepository.save(rule);
        return rule;
    }

    @Transactional
    public Rule updateRule(UUID ruleId, String name, String description, String dataType, String drlContent, String updatedBy) {
        Rule rule = ruleRepository.findById(ruleId)
                .orElseThrow(() -> new IllegalArgumentException("Rule not found with id: " + ruleId));

        // Check if name is being changed and if new name already exists
        if (!rule.getName().equals(name) && ruleRepository.findByName(name).isPresent()) {
            throw new IllegalArgumentException("Rule with name '" + name + "' already exists");
        }

        // Update rule
        rule.setName(name);
        rule.setDescription(description);
        rule.setDataType(dataType);
        rule.setDrlContent(drlContent);
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
        ValidationResult validation = validationService.validateDrl(drlContent, rule.getDataType());
        if (!validation.isValid()) {
            throw new IllegalArgumentException("DRL validation failed: " + String.join(", ", validation.getErrors()));
        }

        // Update rule
        rule.setDrlContent(drlContent);
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

    public Page<Rule> searchRulesWithPagination(String search, String dataType, String status, Integer limit, Integer offset) {
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

}
