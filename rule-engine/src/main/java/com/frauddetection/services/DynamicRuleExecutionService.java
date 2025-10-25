package com.frauddetection.services;

import com.frauddetection.domain.*;
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
        double riskScore;
        try {
            KieContainer kieContainer = buildKieContainerFromRules(rules);
            StatelessKieSession session = kieContainer.newStatelessKieSession();
            session.execute(fact);
            riskScore = fact.getTotalRiskScore();
        } catch (Exception e) {
           throw new RuntimeException("failed to evaluate");
        }

        return Evaluation.builder()
                .riskScore(riskScore)
                .build();
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

        double totalRiskScore = responses.stream()
                .mapToDouble(Evaluation::getRiskScore)
                .sum();
        
        double averageRiskScore = totalRiskScore / responses.size();
        
        int totalViolations = responses.stream()
                .mapToInt(r -> r.getViolations() != null ? r.getViolations().size() : 0)
                .sum();

        return Evaluation.builder()
                .entityId("aggregated")
                .riskScore(averageRiskScore)
                .violations(new ArrayList<>())
                .metadata(EvaluationMetadata.builder()
                        .totalFacts(responses.size())
                        .totalRiskScore(totalRiskScore)
                        .averageRiskScore(averageRiskScore)
                        .totalViolations(totalViolations)
                        .individualResponses(responses.size())
                        .build())
                .build();
    }
}
