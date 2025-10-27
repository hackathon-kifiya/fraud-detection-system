package com.frauddetection.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class SwaggerConfig {

    @Bean
    public OpenAPI ruleEngineOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Rule Engine API")
                        .description("""
                            Rule Engine Service for Fraud Detection System
                            
                            This service provides:
                            - **Rule Management**: Create and manage Drools-based fraud detection rules
                            - **Rule Validation**: Validate DRL syntax and semantics before deployment
                            - **Rule Evaluation**: Execute rules against transaction data to calculate risk scores
                            
                            Note: Data type schemas are managed by the data-management-service.
                            
                            ### Key Features:
                            - Dynamic rule deployment without service restart
                            - DRL validation before activation
                            - Risk scoring based on cumulative violation weights
                            - Support for multiple data types and facts
                            """)
                        .version("0.1.0")
                        .contact(new Contact()
                                .name("Fraud Detection Team")
                                .email("support@frauddetection.com"))
                        .license(new License()
                                .name("Apache 2.0")
                                .url("https://www.apache.org/licenses/LICENSE-2.0.html")))
                .servers(List.of(
                        new Server()
                                .url("http://localhost:8082")
                                .description("Local development server"),
                        new Server()
                                .url("https://api.frauddetection.com")
                                .description("Production server")
                ));
    }
}

