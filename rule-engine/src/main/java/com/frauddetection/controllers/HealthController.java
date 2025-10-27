package com.frauddetection.controllers;

import com.frauddetection.dto.HealthResponseDto;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
@Tag(name = "Health", description = "Health check and service status endpoints")
public class HealthController {

    @Operation(
        summary = "Health check",
        description = "Returns the health status of the rule engine service",
        responses = {
            @ApiResponse(
                responseCode = "200",
                description = "Service is healthy",
                content = @Content(schema = @Schema(implementation = HealthResponseDto.class))
            )
        }
    )
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


