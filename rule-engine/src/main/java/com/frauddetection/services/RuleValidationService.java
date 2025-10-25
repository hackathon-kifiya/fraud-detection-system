package com.frauddetection.services;

import com.frauddetection.domain.Rule;
import com.frauddetection.domain.DynamicFact;
import com.frauddetection.domain.ValidationResult;
import org.kie.api.KieServices;
import org.kie.api.builder.KieBuilder;
import org.kie.api.builder.KieFileSystem;
import org.kie.api.builder.Message;
import org.kie.api.builder.Results;
import org.kie.api.io.ResourceType;
import org.kie.api.runtime.KieContainer;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Service
public class RuleValidationService {

    private static final String PACKAGE_PATTERN = "package\\s+rules\\s*;";

    public ValidationResult validateDrl(String drlContent, String dataType) {
        ValidationResult result = new ValidationResult();
        
        // 1. Basic syntax validation
        if (!validateSyntax(drlContent, result)) {
            return result;
        }
        
        // 2. Package validation
        if (!validatePackage(drlContent, result)) {
            return result;
        }
        
        // 3. Domain class validation
        if (!validateDomainClasses(drlContent, dataType, result)) {
            return result;
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
                return false;
            }
            result.setErrors(errors);
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

    private boolean isValidClassForDataType(String className, String dataType) {
        // For dynamic facts, only DynamicFact is valid
        return "DynamicFact".equals(className);
    }

    // TODO: validate semantics
//    private boolean validateSemantics(String drlContent) {
//        if (drlContent == null || drlContent.isBlank()) {
//            return false;
//        }
//
//        KieServices ks = KieServices.Factory.get();
//        KieFileSystem kfs = ks.newKieFileSystem();
//
//        // Write DRL to virtual file system
//        kfs.write("src/main/resources/temp.drl",
//                ks.getResources()
//                        .newByteArrayResource(drlContent.getBytes())
//                        .setResourceType(ResourceType.DRL));
//
//        // Build — triggers syntax parsing
//        KieBuilder kieBuilder = ks.newKieBuilder(kfs);
//        kieBuilder.buildAll();
//
//        // Return true only if no errors
//        return !kieBuilder.getResults().hasMessages(org.kie.api.builder.Message.Level.ERROR);
//    }
}
