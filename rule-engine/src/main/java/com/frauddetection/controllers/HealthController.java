package com.frauddetection.controllers;

import com.frauddetection.dto.HealthResponseDto;
import org.springframework.http.ResponseEntity;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping
public class HealthController {

    @Autowired
    private com.frauddetection.services.DetectionService detectionService;

    @GetMapping("/health")
    public ResponseEntity<HealthResponseDto> health() {
        return ResponseEntity.ok(HealthResponseDto
                .builder()
                .service("rule-engine")
                .status("healthy")
                .version("0.1.0")
                .build());
    }
}


