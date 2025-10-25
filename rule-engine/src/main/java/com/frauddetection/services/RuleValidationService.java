package com.frauddetection.services;

import com.frauddetection.domain.Rule;
import com.frauddetection.domain.DynamicFact;
import org.kie.api.KieServices;
import org.kie.api.builder.KieBuilder;
import org.kie.api.builder.KieFileSystem;
import org.kie.api.builder.Message;
import org.kie.api.builder.Results;
import org.kie.api.runtime.KieContainer;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Service
public class RuleValidationService {

    private static final String PACKAGE_PATTERN = "package\\s+rules\\s*;";
    private static final Pattern CLASS_REFERENCE_PATTERN = Pattern.compile("\\bDynamicFact\\b");

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
        
        // 4. Semantic validation with test data
        if (!validateSemantics(drlContent, dataType, result)) {
            return result;
        }
        
        result.setValid(true);
        return result;
    }

    private boolean validateSyntax(String drlContent, ValidationResult result) {
        try {
            KieServices kieServices = KieServices.Factory.get();
            KieFileSystem kieFileSystem = kieServices.newKieFileSystem();
            kieFileSystem.write("src/main/resources/rules/validation.drl", drlContent);
            
            KieBuilder kieBuilder = kieServices.newKieBuilder(kieFileSystem);
            kieBuilder.buildAll();
            
            Results results = kieBuilder.getResults();
            if (results.hasMessages(Message.Level.ERROR)) {
                for (Message message : results.getMessages(Message.Level.ERROR)) {
                    result.addError("Syntax Error: " + message.getText());
                }
                return false;
            }
            
            return true;
        } catch (Exception e) {
            result.addError("Syntax validation failed: " + e.getMessage());
            return false;
        }
    }

    private boolean validatePackage(String drlContent, ValidationResult result) {
        Pattern packagePattern = Pattern.compile(PACKAGE_PATTERN);
        if (!packagePattern.matcher(drlContent).find()) {
            result.addError("DRL must contain 'package rules;' declaration");
            return false;
        }
        return true;
    }

    private boolean validateDomainClasses(String drlContent, String dataType, ValidationResult result) {
        // For dynamic facts, we expect DynamicFact class references
        if (!drlContent.contains("DynamicFact")) {
            result.addError("DRL must reference DynamicFact class for dynamic data evaluation");
            return false;
        }
        
        // Check for proper package import
        if (!drlContent.contains("import com.frauddetection.domain.DynamicFact")) {
            result.addError("DRL must import com.frauddetection.domain.DynamicFact");
            return false;
        }
        
        return true;
    }

    private boolean isValidClassForDataType(String className, String dataType) {
        // For dynamic facts, only DynamicFact is valid
        return "DynamicFact".equals(className);
    }

    private boolean validateSemantics(String drlContent, String dataType, ValidationResult result) {
        try {
            // Create test data based on data type
            Object testData = createTestData(dataType);
            if (testData == null) {
                result.addError("Could not create test data for validation");
                return false;
            }
            
            // Compile and test the rule
            KieServices kieServices = KieServices.Factory.get();
            KieFileSystem kieFileSystem = kieServices.newKieFileSystem();
            kieFileSystem.write("src/main/resources/rules/semantic_test.drl", drlContent);
            
            KieBuilder kieBuilder = kieServices.newKieBuilder(kieFileSystem);
            kieBuilder.buildAll();
            
            Results results = kieBuilder.getResults();
            if (results.hasMessages(Message.Level.ERROR)) {
                for (Message message : results.getMessages(Message.Level.ERROR)) {
                    result.addError("Semantic Error: " + message.getText());
                }
                return false;
            }
            
            // Test execution with sample data
            KieContainer kieContainer = kieServices.newKieContainer(kieBuilder.getKieModule().getReleaseId());
            kieContainer.newStatelessKieSession().execute(testData);
            
            return true;
        } catch (Exception e) {
            result.addError("Semantic validation failed: " + e.getMessage());
            return false;
        }
    }

    private Object createTestData(String dataType) {
        DynamicFact fact = new DynamicFact("test-entity", dataType.toLowerCase());
        
        // Create generic test data based on common patterns
        switch (dataType.toLowerCase()) {
            case "transaction":
                fact.setProperty("amount", 1000.0);
                fact.setProperty("accountBalance", 500.0);
                fact.setProperty("type", "debit");
                fact.setProperty("paymentMethod", "card");
                break;
            case "kyc":
                fact.setProperty("verifiedStatus", false);
                fact.setProperty("verificationDate", "2023-01-01");
                break;
            case "loan":
                fact.setProperty("amount", 60000.0);
                fact.setProperty("term", 36);
                fact.setProperty("interestRate", 5.5);
                break;
            case "credit":
                fact.setProperty("score", 650);
                fact.setProperty("historyLength", 24);
                fact.setProperty("delinquencies", 0);
                break;
            case "repayment":
                fact.setProperty("amount", 500.0);
                fact.setProperty("dueDate", "2023-12-01");
                fact.setProperty("isLate", false);
                break;
            default:
                // For custom data types, create generic test data
                fact.setProperty("amount", 100.0);
                fact.setProperty("status", "active");
                fact.setProperty("timestamp", java.time.Instant.now());
                break;
        }
        
        return fact;
    }

    public static class ValidationResult {
        private boolean valid = false;
        private List<String> errors = new ArrayList<>();
        private List<String> warnings = new ArrayList<>();

        public boolean isValid() { return valid; }
        public void setValid(boolean valid) { this.valid = valid; }

        public List<String> getErrors() { return errors; }
        public void addError(String error) { this.errors.add(error); }

        public List<String> getWarnings() { return warnings; }
        public void addWarning(String warning) { this.warnings.add(warning); }

        public boolean hasErrors() { return !errors.isEmpty(); }
        public boolean hasWarnings() { return !warnings.isEmpty(); }
    }
}
