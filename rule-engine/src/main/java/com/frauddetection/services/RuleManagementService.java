package com.frauddetection.services;

import com.frauddetection.domain.DataType;
import com.frauddetection.domain.Rule;
import com.frauddetection.domain.ValidationResult;
import com.frauddetection.dto.RuleRequestDto;
import com.frauddetection.dto.RuleResponseDto;
import com.frauddetection.exceptions.RuleNotFoundException;
import com.frauddetection.exceptions.ValidationException;
import com.frauddetection.mapper.RuleMapper;
import com.frauddetection.repository.RuleRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Service
public class RuleManagementService {

    @Autowired
    private RuleRepository ruleRepository;

    @Autowired
    private RuleValidationService validationService;

    @Autowired
    private RuleMapper ruleMapper;
    
    @Autowired
    private DataTypeService dataTypeService;
    
    public RuleResponseDto getRuleById(UUID id) {
        Rule rule = ruleRepository.findById(id)
                .orElseThrow(() -> new RuleNotFoundException("Rule not found with id: " + id));
        return ruleMapper.toDto(rule);
    }

    @Transactional
    public RuleResponseDto createRule(RuleRequestDto request) {
        // Validate data type exists (enforce association)
        if (request.getDataType() == null || request.getDataType().trim().isEmpty()) {
            throw new ValidationException("Data type is required for rule creation");
        }
        
        // Check if data type exists
        DataType dataType = dataTypeService.getDataTypeEntity(request.getDataType());
        if (dataType == null) {
            throw new ValidationException("Data type '" + request.getDataType() + "' does not exist. Please create it first.");
        }
        
        // Validate DRL syntax and semantics
        ValidationResult validation = validationService.validateDrl(request.getDrlContent(), request.getDataType());
        if (!validation.isValid()) {
            throw new ValidationException("DRL validation failed: " + String.join(", ", validation.getErrors()));
        }
        
        // Semantic validation: validate field names against schema
        validateSchemaSemantics(request.getDrlContent(), dataType);

        Rule rule = ruleMapper.toEntity(request);
        // Don't set ID - let database generate it with DEFAULT uuid_generate_v4()
        rule.setCreatedAt(Instant.now());
        rule.setUpdatedAt(Instant.now());
        if (rule.getStatus() == null) {
            rule.setStatus(Rule.Status.ACTIVE);
        }
        
        // Associate rule with data type (already done via dataType field)
        rule.setDataType(request.getDataType());
        
        // Use save method (insert/update handled by repository)
        rule = ruleRepository.save(rule);
        
        return ruleMapper.toDto(rule);
    }
    
    /**
     * Validates semantic aspects of the DRL against the data type schema.
     * Extracts field names from DRL conditions and validates against schema.
     */
    private void validateSchemaSemantics(String drlContent, DataType dataType) {
        if (dataType.getSchemaDefinition() == null) {
            return; // No schema defined, skip semantic validation
        }
        
        // Parse schema to get field definitions
        Map<String, Object> schemaMap = parseSchemaFromJson(dataType.getSchemaDefinition());
        if (schemaMap == null || !schemaMap.containsKey("fields")) {
            return; // No fields defined in schema
        }
        
        @SuppressWarnings("unchecked")
        Map<String, Object> fields = (Map<String, Object>) schemaMap.get("fields");
        if (fields == null || fields.isEmpty()) {
            return;
        }
        
        // Extract field names from DRL
        Set<String> referencedFields = extractFieldReferences(drlContent);
        
        // Validate referenced fields exist in schema
        for (String field : referencedFields) {
            if (!fields.containsKey(field)) {
                throw new ValidationException(
                    String.format(
                        "Field '%s' is referenced in the rule but is not defined in the data type schema for '%s'. " +
                        "Available fields: %s",
                        field, dataType.getDataType(), fields.keySet()
                    )
                );
            }
        }
        
        // Optional: Validate required fields are checked in rules
        // (This can be a warning rather than an error)
        validateRequiredFields(drlContent, schemaMap, dataType.getDataType());
    }
    
    private Map<String, Object> parseSchemaFromJson(String jsonSchema) {
        if (jsonSchema == null || jsonSchema.trim().isEmpty()) {
            return null;
        }
        try {
            com.fasterxml.jackson.databind.ObjectMapper mapper = new com.fasterxml.jackson.databind.ObjectMapper();
            return mapper.readValue(jsonSchema, new com.fasterxml.jackson.core.type.TypeReference<Map<String, Object>>() {});
        } catch (Exception e) {
            throw new ValidationException("Invalid schema definition JSON: " + e.getMessage());
        }
    }
    
    /**
     * Extracts field references from DRL content.
     * Looks for patterns like:
     * - properties["fieldName"] or properties['fieldName']
     * - getPropertyAsNumber("fieldName")
     * - getPropertyAsString("fieldName")
     * - hasProperty("fieldName")
     */
    private Set<String> extractFieldReferences(String drlContent) {
        Set<String> fields = new HashSet<>();
        
        // Pattern 1: properties["fieldName"] or properties['fieldName']
        Pattern pattern1 = Pattern.compile(
            "properties\\s*\\[\"([^\"]+)\"\\]|properties\\s*\\['([^']+)'\\]"
        );
        
        Matcher matcher1 = pattern1.matcher(drlContent);
        while (matcher1.find()) {
            String field = matcher1.group(1) != null ? matcher1.group(1) : matcher1.group(2);
            if (field != null && !field.isEmpty()) {
                fields.add(field);
            }
        }
        
        // Pattern 2: getPropertyAsNumber("fieldName"), getPropertyAsString("fieldName"), hasProperty("fieldName")
        Pattern pattern2 = Pattern.compile(
            "(?:getPropertyAsNumber|getPropertyAsString|hasProperty)\\s*\\(\"([^\"]+)\"\\s*\\)"
        );
        
        Matcher matcher2 = pattern2.matcher(drlContent);
        while (matcher2.find()) {
            String field = matcher2.group(1);
            if (field != null && !field.isEmpty()) {
                fields.add(field);
            }
        }
        
        return fields;
    }
    
    private void validateRequiredFields(String drlContent, Map<String, Object> schemaMap, String dataType) {
        if (!schemaMap.containsKey("required")) {
            return;
        }
        
        Object requiredObj = schemaMap.get("required");
        if (!(requiredObj instanceof List)) {
            return;
        }
        
        List<?> required = (List<?>) requiredObj;
        Set<String> referencedFields = extractFieldReferences(drlContent);
        
        // Check if required fields are referenced
        for (Object reqField : required) {
            if (!referencedFields.contains(reqField.toString())) {
                // This is just a warning, not an error
                // Required fields should ideally be checked in rules
            }
        }
    }

    @Transactional
    public RuleResponseDto updateRule(UUID ruleId, RuleRequestDto request, String updatedBy) {
        // Find existing rule
        Rule rule = ruleRepository.findById(ruleId)
                .orElseThrow(() -> new RuleNotFoundException("Rule not found with id: " + ruleId));

        // Validate DRL content if provided
        if (request.getDrlContent() != null && !request.getDrlContent().trim().isEmpty()) {
            ValidationResult validation = validationService.validateDrl(request.getDrlContent(), request.getDataType());
            if (!validation.isValid()) {
                throw new ValidationException("DRL validation failed: " + String.join(", ", validation.getErrors()));
            }
        }

        // Check if name is being changed and if new name already exists
        if (request.getName() != null && !rule.getName().equals(request.getName()) 
                && ruleRepository.findByName(request.getName()).isPresent()) {
            throw new ValidationException("Rule with name '" + request.getName() + "' already exists");
        }

        // Update rule fields
        if (request.getName() != null) {
            rule.setName(request.getName());
        }
        if (request.getDescription() != null) {
            rule.setDescription(request.getDescription());
        }
        if (request.getDataType() != null) {
            rule.setDataType(request.getDataType());
        }
        if (request.getDrlContent() != null) {
            rule.setDrlContent(request.getDrlContent());
        }
        
        rule.setUpdatedAt(Instant.now());
        rule.setUpdatedBy(updatedBy);
        
        Rule savedRule = ruleRepository.save(rule);
        return ruleMapper.toDto(savedRule);
    }

    @Transactional
    public void deleteRule(UUID ruleId) {
        Rule rule = ruleRepository.findById(ruleId)
                .orElseThrow(() -> new RuleNotFoundException("Rule not found with id: " + ruleId));

        // Soft delete - set status to inactive
        rule.setStatus(Rule.Status.INACTIVE);
        rule.setUpdatedAt(Instant.now());
        ruleRepository.save(rule);
    }

    @Transactional
    public RuleResponseDto activateRule(UUID ruleId) {
        Rule rule = ruleRepository.findById(ruleId)
                .orElseThrow(() -> new RuleNotFoundException("Rule not found with id: " + ruleId));

        rule.setStatus(Rule.Status.ACTIVE);
        rule.setUpdatedAt(Instant.now());
        Rule savedRule = ruleRepository.save(rule);
        return ruleMapper.toDto(savedRule);
    }

    @Transactional
    public RuleResponseDto deactivateRule(UUID ruleId) {
        Rule rule = ruleRepository.findById(ruleId)
                .orElseThrow(() -> new RuleNotFoundException("Rule not found with id: " + ruleId));

        rule.setStatus(Rule.Status.INACTIVE);
        rule.setUpdatedAt(Instant.now());
        Rule savedRule = ruleRepository.save(rule);
        return ruleMapper.toDto(savedRule);
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
        
        List<Rule> rules;
        long totalCount;
        
        // Handle search with filters
        if (search != null && !search.trim().isEmpty()) {
            if (dataType != null && status != null) {
                rules = ruleRepository.findByNameOrDescriptionContainingIgnoreCaseAndDataTypeAndStatusWithPagination(
                    "%" + search + "%", dataType, status, limitValue, offsetValue);
                totalCount = countRules(search, dataType, status);
            } else if (dataType != null) {
                rules = ruleRepository.findByNameOrDescriptionContainingIgnoreCaseAndDataTypeWithPagination(
                    "%" + search + "%", dataType, limitValue, offsetValue);
                totalCount = countRules(search, dataType, null);
            } else if (status != null) {
                rules = ruleRepository.findByNameOrDescriptionContainingIgnoreCaseAndStatusWithPagination(
                    "%" + search + "%", status, limitValue, offsetValue);
                totalCount = countRules(search, null, status);
            } else {
                rules = ruleRepository.findByNameOrDescriptionContainingIgnoreCaseWithPagination(
                    "%" + search + "%", limitValue, offsetValue);
                totalCount = countRules(search, null, null);
            }
        } else {
            // Handle filters without search
            if (dataType != null && status != null) {
                rules = ruleRepository.findByDataTypeAndStatusWithPagination(dataType, status, limitValue, offsetValue);
                totalCount = countRules(null, dataType, status);
            } else if (dataType != null) {
                rules = ruleRepository.findByDataTypeWithPagination(dataType, limitValue, offsetValue);
                totalCount = countRules(null, dataType, null);
            } else if (status != null) {
                rules = ruleRepository.findByStatusWithPagination(status, limitValue, offsetValue);
                totalCount = countRules(null, null, status);
            } else {
                rules = ruleRepository.findAllOrderByCreatedAtWithPagination(limitValue, offsetValue);
                totalCount = countAll();
            }
        }
        
        return new PageImpl<>(rules, PageRequest.of(offsetValue / limitValue, limitValue), totalCount);
    }
    
    private long countRules(String search, String dataType, String status) {
        if (search != null && !search.trim().isEmpty()) {
            if (dataType != null && status != null) {
                return ruleRepository.findByNameOrDescriptionContainingIgnoreCaseAndDataTypeAndStatusWithPagination(
                    "%" + search + "%", dataType, status, Integer.MAX_VALUE, 0).size();
            } else if (dataType != null) {
                return ruleRepository.findByNameOrDescriptionContainingIgnoreCaseAndDataTypeWithPagination(
                    "%" + search + "%", dataType, Integer.MAX_VALUE, 0).size();
            } else if (status != null) {
                return ruleRepository.findByNameOrDescriptionContainingIgnoreCaseAndStatusWithPagination(
                    "%" + search + "%", status, Integer.MAX_VALUE, 0).size();
            } else {
                return ruleRepository.findByNameOrDescriptionContainingIgnoreCaseWithPagination(
                    "%" + search + "%", Integer.MAX_VALUE, 0).size();
            }
        }
        return countAll();
    }
    
    private long countAll() {
        return ((List<Rule>) ruleRepository.findAll()).size();
    }

    public Map<String, Object> validateDrlContent(String drlContent, String dataType) {
        Map<String, Object> result = new java.util.HashMap<>();
        List<String> allErrors = new ArrayList<>();
        
        // Validate data type exists if provided
        if (dataType != null && !dataType.trim().isEmpty()) {
            DataType dataTypeEntity = dataTypeService.getDataTypeEntity(dataType);
            if (dataTypeEntity == null) {
                result.put("valid", false);
                result.put("errors", List.of("Data type '" + dataType + "' does not exist"));
                return result;
            }
        }
        
        // Step 1: Validate DRL syntax, package, and domain classes
        ValidationResult syntaxValidation = validationService.validateDrl(drlContent, dataType);
        
        if (!syntaxValidation.isValid()) {
            allErrors.addAll(syntaxValidation.getErrors());
        }
        
        // Step 2: Semantic validation - validate field names against schema if data type is provided
        if (dataType != null && !dataType.trim().isEmpty() && syntaxValidation.isValid()) {
            DataType dataTypeEntity = dataTypeService.getDataTypeEntity(dataType);
            if (dataTypeEntity != null && dataTypeEntity.getSchemaDefinition() != null) {
                try {
                    validateSchemaSemantics(drlContent, dataTypeEntity);
                } catch (ValidationException e) {
                    allErrors.add(e.getMessage());
                }
            }
        }
        
        // Return combined results
        result.put("valid", allErrors.isEmpty());
        result.put("errors", allErrors);
        
        return result;
    }

}
