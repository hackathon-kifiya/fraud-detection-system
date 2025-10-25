package com.frauddetection.services;

import com.frauddetection.domain.DynamicFact;
import com.frauddetection.domain.EvaluationRequest;
import com.frauddetection.domain.EvaluationResponse;
import com.frauddetection.domain.Rule;
import com.frauddetection.domain.Violation;
import com.frauddetection.repository.RuleRepository;
import org.kie.api.KieServices;
import org.kie.api.builder.KieBuilder;
import org.kie.api.builder.KieFileSystem;
import org.kie.api.builder.Message;
import org.kie.api.builder.Results;
import org.kie.api.runtime.KieContainer;
import org.kie.api.runtime.StatelessKieSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class DynamicRuleExecutionService {

    @Autowired
    private RuleRepository ruleRepository;

    public EvaluationResponse evaluateFacts(EvaluationRequest request) {
        // Get active rules for the data type
        List<Rule> activeRules = ruleRepository.findActiveRulesByDataType(request.getDataType());
        
        if (activeRules.isEmpty()) {
            return createEmptyResponse("No active rules found for data type: " + request.getDataType());
        }

        // Convert request facts to DynamicFact objects
        List<DynamicFact> facts = convertToDynamicFacts(request);
        
        // Execute rules against each fact
        List<EvaluationResponse> responses = new ArrayList<>();
        
        for (DynamicFact fact : facts) {
            EvaluationResponse response = evaluateFact(fact, activeRules);
            responses.add(response);
        }

        // If single fact, return single response
        if (responses.size() == 1) {
            return responses.get(0);
        }

        // Multiple facts - return aggregated response
        return aggregateResponses(responses);
    }

    private EvaluationResponse evaluateFact(DynamicFact fact, List<Rule> rules) {
        try {
            // Build KieBase from rules
            KieContainer kieContainer = buildKieContainerFromRules(rules);
            StatelessKieSession session = kieContainer.newStatelessKieSession();

            // Execute rules against the fact
            session.execute(fact);

            // Calculate risk score and verdict
            double riskScore = fact.getTotalRiskScore();
            // Rule engine only calculates risk score, verdict is determined by backend
            return new EvaluationResponse(
                fact.getEntityId(),
                riskScore,
                new ArrayList<>(fact.getViolations()),
                EvaluationResponse.Verdict.APPROVE
            );

        } catch (Exception e) {
            // Return error response
            EvaluationResponse errorResponse = new EvaluationResponse(
                fact.getEntityId(),
                0.0,
                new ArrayList<>(),
                EvaluationResponse.Verdict.REVIEW
            );
            
            Map<String, Object> metadata = new HashMap<>();
            metadata.put("error", "Rule execution failed: " + e.getMessage());
            errorResponse.setMetadata(metadata);
            
            return errorResponse;
        }
    }

    private KieContainer buildKieContainerFromRules(List<Rule> rules) {
        KieServices kieServices = KieServices.Factory.get();
        KieFileSystem kieFileSystem = kieServices.newKieFileSystem();

        // Add each rule to the file system
        for (int i = 0; i < rules.size(); i++) {
            Rule rule = rules.get(i);
            String fileName = "src/main/resources/rules/dynamic_" + rule.getName().replaceAll("\\s+", "_") + "_" + i + ".drl";
            kieFileSystem.write(fileName, rule.getDrlContent());
        }

        // Build the container
        KieBuilder kieBuilder = kieServices.newKieBuilder(kieFileSystem);
        kieBuilder.buildAll();

        Results results = kieBuilder.getResults();
        if (results.hasMessages(Message.Level.ERROR)) {
            StringBuilder errorMsg = new StringBuilder("Rule compilation errors: ");
            for (Message message : results.getMessages(Message.Level.ERROR)) {
                errorMsg.append(message.getText()).append("; ");
            }
            throw new RuntimeException(errorMsg.toString());
        }

        return kieServices.newKieContainer(kieBuilder.getKieModule().getReleaseId());
    }

    private List<DynamicFact> convertToDynamicFacts(EvaluationRequest request) {
        List<DynamicFact> facts = new ArrayList<>();
        
        for (Map<String, Object> factData : request.getFacts()) {
            DynamicFact fact = new DynamicFact();
            
            // Extract entity ID if present
            String entityId = (String) factData.get("entityId");
            if (entityId == null) {
                entityId = java.util.UUID.randomUUID().toString();
            }
            fact.setEntityId(entityId);
            fact.setDataType(request.getDataType().toLowerCase());
            
            // Copy all properties
            for (Map.Entry<String, Object> entry : factData.entrySet()) {
                if (!"entityId".equals(entry.getKey())) {
                    fact.setProperty(entry.getKey(), entry.getValue());
                }
            }
            
            facts.add(fact);
        }
        
        return facts;
    }


    private EvaluationResponse createEmptyResponse(String message) {
        EvaluationResponse response = new EvaluationResponse(
            "unknown",
            0.0,
            new ArrayList<>(),
            EvaluationResponse.Verdict.APPROVE
        );
        
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("message", message);
        response.setMetadata(metadata);
        
        return response;
    }

    private EvaluationResponse aggregateResponses(List<EvaluationResponse> responses) {
        if (responses.isEmpty()) {
            return createEmptyResponse("No responses to aggregate");
        }

        // Calculate aggregate metrics
        double totalRiskScore = responses.stream()
                .mapToDouble(EvaluationResponse::getRiskScore)
                .sum();
        
        double averageRiskScore = totalRiskScore / responses.size();
        
        int totalViolations = responses.stream()
                .mapToInt(r -> r.getViolations() != null ? r.getViolations().size() : 0)
                .sum();

        // Rule engine only calculates risk score, verdict is determined by backend
        EvaluationResponse.Verdict overallVerdict = EvaluationResponse.Verdict.APPROVE;

        // Create aggregated response
        EvaluationResponse aggregated = new EvaluationResponse(
            "aggregated",
            averageRiskScore,
            new ArrayList<>(), // Individual violations not aggregated
            overallVerdict
        );

        Map<String, Object> metadata = new HashMap<>();
        metadata.put("totalFacts", responses.size());
        metadata.put("totalRiskScore", totalRiskScore);
        metadata.put("averageRiskScore", averageRiskScore);
        metadata.put("totalViolations", totalViolations);
        metadata.put("individualResponses", responses);
        aggregated.setMetadata(metadata);

        return aggregated;
    }
}
