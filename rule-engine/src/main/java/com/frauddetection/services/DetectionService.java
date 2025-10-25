package com.frauddetection.services;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.kie.api.runtime.StatelessKieSession;
import org.kie.api.KieServices;
import org.kie.api.runtime.KieContainer;
import org.springframework.stereotype.Service;

import com.frauddetection.domain.DynamicFact;

@Service
public class DetectionService {

    private final StatelessKieSession session;

    public DetectionService() {
        KieServices ks = KieServices.Factory.get();
        KieContainer container = ks.getKieClasspathContainer();
        this.session = container.newStatelessKieSession("fraudKSession");
    }

    public Map<String, Object> detect(int daysBack, List<Object> facts) {
        session.execute(facts);

        int flagged = 0;
        for (Object f : facts) {
            if (f instanceof DynamicFact fact && fact.hasViolations()) {
                flagged++;
            }
        }

        Map<String, Object> summary = new HashMap<>();
        summary.put("processed_days", daysBack);
        summary.put("flagged_count", flagged);

        Map<String, Object> result = new HashMap<>();
        result.put("summary", summary);
        return result;
    }
}


