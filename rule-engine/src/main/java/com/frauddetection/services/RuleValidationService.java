package com.frauddetection.services;

import com.frauddetection.domain.DataType;
import com.frauddetection.domain.ValidationResult;
import com.frauddetection.exceptions.ValidationException;
import com.frauddetection.repository.DataTypeRepository;
import org.kie.api.KieServices;
import org.kie.api.builder.KieBuilder;
import org.kie.api.builder.KieFileSystem;
import org.kie.api.builder.Message;
import org.kie.api.builder.Results;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Service
public class RuleValidationService {

    private static final String PACKAGE_PATTERN = "package\\s+rules\\s*;";

    @Autowired
    private DataTypeRepository dataTypeRepository;

    public ValidationResult validateDrl(String drlContent, String dataType) {
        ValidationResult result = new ValidationResult();
        
        // 1. Package validation (check first before syntax validation)
        if (!validatePackage(drlContent, result)) {
            return result;
        }
        
        // 2. Domain class validation (check before syntax validation)
        if (!validateDomainClasses(drlContent, dataType, result)) {
            return result;
        }
        
        // 3. Basic syntax validation (use Drools compiler)
        if (!validateSyntax(drlContent, result)) {
            return result;
        }
        
        // 4. Semantic validation - validate field names against schema
        if (dataType != null && !dataType.trim().isEmpty()) {
            if (!validateSemantics(drlContent, dataType, result)) {
                return result;
            }
        }
        
        result.setValid(true);
        return result;
    }

    private boolean validateSyntax(String drlContent, ValidationResult result) {
        List<String> errors = new ArrayList<>();
        try {
            KieServices kieServices = KieServices.Factory.get();
            KieFileSystem kieFileSystem = kieServices.newKieFileSystem();
            kieFileSystem.write("src/main/resources/rules/validation.drl", drlContent);
            
            KieBuilder kieBuilder = kieServices.newKieBuilder(kieFileSystem);
            kieBuilder.buildAll();
            
            Results results = kieBuilder.getResults();
            if (results.hasMessages(Message.Level.ERROR)) {
                for (Message message : results.getMessages(Message.Level.ERROR)) {
                    errors.add("Syntax Error: " + message.getText());
                }
                result.setErrors(errors);
                return false;
            }
            // No syntax errors, don't modify existing errors
            return true;
        } catch (Exception e) {
            errors.add("Syntax validation failed: " + e.getMessage());
            result.setErrors(errors);
            return false;
        }
    }

    private boolean validatePackage(String drlContent, ValidationResult result) {
        Pattern packagePattern = Pattern.compile(PACKAGE_PATTERN);
        List<String> errors = new ArrayList<>();
        if (!packagePattern.matcher(drlContent).find()) {
            errors.add("DRL must contain 'package rules;' declaration");
            result.setErrors(errors);
            return false;
        }
        return true;
    }

    private boolean validateDomainClasses(String drlContent, String dataType, ValidationResult result) {
        List<String> errors = new ArrayList<>();
        if (!drlContent.contains("DynamicFact")) {
            errors.add("DRL must reference DynamicFact class for dynamic data evaluation");
            result.setErrors(errors);
            return false;
        }
        
        // Check for proper package import
        if (!drlContent.contains("import com.frauddetection.domain.DynamicFact")) {
            errors.add("DRL must import com.frauddetection.domain.DynamicFact");
            result.setErrors(errors);
            return false;
        }
        
        return true;
    }

    /**
     * Validates semantic aspects of the DRL against the data type schema.
     * Extracts field names from DRL conditions and validates against schema.
     */
    private boolean validateSemantics(String drlContent, String dataType, ValidationResult result) {
        List<String> errors = new ArrayList<>();
        
        // Get data type from database
        DataType dataTypeEntity = dataTypeRepository.findByDataType(dataType).orElse(null);
        if (dataTypeEntity == null) {
            // Data type doesn't exist - this will be caught by createRule flow
            return true; // Let createRule handle this error
        }
        
        if (dataTypeEntity.getSchemaDefinition() == null) {
            return true; // No schema defined, skip semantic validation
        }
        
        try {
            // Parse schema to get field definitions
            Map<String, Object> schemaMap = parseSchemaFromJson(dataTypeEntity.getSchemaDefinition());
            if (schemaMap == null || !schemaMap.containsKey("fields")) {
                return true; // No fields defined in schema
            }
            
            @SuppressWarnings("unchecked")
            Map<String, Object> fields = (Map<String, Object>) schemaMap.get("fields");
            if (fields == null || fields.isEmpty()) {
                return true;
            }
            
            // Extract field names from DRL
            Set<String> referencedFields = extractFieldReferences(drlContent);
            
            // Validate referenced fields exist in schema
            for (String field : referencedFields) {
                if (!fields.containsKey(field)) {
                    errors.add(String.format(
                        "Field '%s' is referenced in the rule but is not defined in the data type schema for '%s'. Available fields: %s",
                        field, dataType, fields.keySet()
                    ));
                }
            }
            
            if (!errors.isEmpty()) {
                result.setErrors(errors);
                return false;
            }
            
            return true;
        } catch (Exception e) {
            errors.add("Semantic validation failed: " + e.getMessage());
            result.setErrors(errors);
            return false;
        }
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

}
