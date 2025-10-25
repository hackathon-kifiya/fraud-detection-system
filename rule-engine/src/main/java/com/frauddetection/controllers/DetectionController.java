package com.frauddetection.controllers;

import java.util.HashMap;
import java.util.Map;

import org.springframework.http.ResponseEntity;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping
public class DetectionController {

    @Autowired
    private com.frauddetection.services.DetectionService detectionService;

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> resp = new HashMap<>();
        resp.put("service", "java-engine");
        resp.put("version", "0.1.0");
        resp.put("status", "healthy");
        return ResponseEntity.ok(resp);
    }

    @PostMapping("/api/detect")
    public ResponseEntity<Map<String, Object>> detect(@RequestBody(required = false) Map<String, Object> body) {
        int daysBack = 30;
        if (body != null && body.get("days_back") instanceof Number) {
            daysBack = ((Number) body.get("days_back")).intValue();
        }

        // TODO: Load facts from DB (transactions, loans, etc.)
        java.util.List<Object> facts = new java.util.ArrayList<>();
        Map<String, Object> result = detectionService.detect(daysBack, facts);

        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "Detection executed (stub)");
        response.put("result", result);
        return ResponseEntity.ok(response);
    }
}


