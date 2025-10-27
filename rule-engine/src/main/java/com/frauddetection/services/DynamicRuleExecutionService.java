package com.frauddetection.services;

import com.frauddetection.domain.*;
import com.frauddetection.exceptions.RuleExecutionException;
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
import java.util.List;
import java.util.Map;

@Service
public class DynamicRuleExecutionService {

    @Autowired
    private RuleRepository ruleRepository;

    public Evaluation evaluateFacts(EvaluationQuery request) {
        Evaluation response;
        List<Rule> activeRules = ruleRepository.findActiveRulesByDataType(request.getDataType());

        List<DynamicFact> facts = convertToDynamicFacts(request);
        List<Evaluation> responses = new ArrayList<>();

        for (DynamicFact fact : facts) {
            response = evaluateFact(fact, activeRules);
            responses.add(response);
        }

        return aggregateResponses(responses);
    }

    private Evaluation evaluateFact(DynamicFact fact, List<Rule> rules) {
        try {
            KieContainer kieContainer = buildKieContainerFromRules(rules);
            StatelessKieSession session = kieContainer.newStatelessKieSession();
            
            // Make sure violations list is initialized
            if (fact.getViolations() == null) {
                fact.setViolations(new ArrayList<>());
            }
            
            session.execute(fact);
            double riskScore = fact.getTotalRiskScore();
            
            // Debug: Get violations count
            int violationsCount = (fact.getViolations() != null) ? fact.getViolations().size() : 0;
            System.out.println("DEBUG: Fact violations count: " + violationsCount + ", Risk score: " + riskScore);
            if (violationsCount > 0) {
                System.out.println("DEBUG: First violation: " + fact.getViolations().get(0));
            }

            return Evaluation.builder()
                    .entityId(fact.getEntityId())
                    .riskScore(riskScore)
                    .violations(fact.getViolations())
                    .build();
        } catch (Exception e) {
            // Let the exception propagate to controller advice
            throw new RuleExecutionException("Failed to evaluate fact: " + e.getMessage(), e);
        }
    }

    /**
     * Builds a Drools KieContainer from rules stored in the database.
     * Note: Rules are stored as strings in DB, but Drools requires them in a virtual file system
     * (not actual disk files) for compilation and execution.
     * 
     * @param rules - Rules loaded from database
     * @return Compiled KieContainer ready for rule execution
     */
    private KieContainer buildKieContainerFromRules(List<Rule> rules) {
        KieServices kieServices = KieServices.Factory.get();
        // Create virtual file system (not actual files - in-memory only)
        KieFileSystem kieFileSystem = kieServices.newKieFileSystem();

        // Register each rule from database into the virtual file system
        for (int i = 0; i < rules.size(); i++) {
            Rule rule = rules.get(i);
            // Virtual path - used by Drools for compilation, not a real file path
            String virtualPath = "src/main/resources/rules/dynamic_" + rule.getName().replaceAll("\\s+", "_") + "_" + i + ".drl";
            // Write rule content to virtual file system
            kieFileSystem.write(virtualPath, rule.getDrlContent());
        }

        // Compile all rules in the virtual file system
        KieBuilder kieBuilder = kieServices.newKieBuilder(kieFileSystem);
        kieBuilder.buildAll();

        // Check for compilation errors
        Results results = kieBuilder.getResults();
        if (results.hasMessages(Message.Level.ERROR)) {
            StringBuilder errorMsg = new StringBuilder("Rule compilation errors: ");
            for (Message message : results.getMessages(Message.Level.ERROR)) {
                errorMsg.append(message.getText()).append("; ");
            }
            throw new RuleExecutionException(errorMsg.toString());
        }

        return kieServices.newKieContainer(kieBuilder.getKieModule().getReleaseId());
    }

    private List<DynamicFact> convertToDynamicFacts(EvaluationQuery request) {
        List<DynamicFact> facts = new ArrayList<>();
        
        for (Map<String, Object> factData : request.getFacts()) {
            // Extract entity ID if present
            String entityId = (String) factData.get("entityId");
            if (entityId == null) {
                entityId = java.util.UUID.randomUUID().toString();
            }
            
            DynamicFact fact = new DynamicFact(entityId, request.getDataType().toLowerCase());
            
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


    private Evaluation aggregateResponses(List<Evaluation> responses) {
        // Define maximum possible risk score
        // This represents the worst-case scenario with all violations triggered
        final double MAX_POSSIBLE_SCORE = 20.0;
        
        double totalRiskScore = responses.stream()
                .mapToDouble(Evaluation::getRiskScore)
                .sum();
        
        double averageRiskScore = totalRiskScore / responses.size();
        
        // Normalize risk score to 0-1 scale
        double normalizedRiskScore = Math.min(1.0, averageRiskScore / MAX_POSSIBLE_SCORE);
        
        // Collect all violations from all responses
        List<Violation> allViolations = new ArrayList<>();
        for (Evaluation response : responses) {
            if (response.getViolations() != null) {
                allViolations.addAll(response.getViolations());
            }
        }
        
        int totalViolations = allViolations.size();

        return Evaluation.builder()
                .entityId("aggregated")
                .riskScore(averageRiskScore)
                .violations(allViolations)
                .metadata(EvaluationMetadata.builder()
                        .totalFacts(responses.size())
                        .totalRiskScore(totalRiskScore)
                        .averageRiskScore(averageRiskScore)
                        .normalizedRiskScore(normalizedRiskScore)
                        .totalViolations(totalViolations)
                        .individualResponses(responses.size())
                        .build())
                .build();
    }
}
