package com.frauddetection.client;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;

import java.util.Map;

/**
 * HTTP client for communicating with the data-management-service.
 * Fetches data type schemas for rule validation.
 */
@Component
public class DataManagementClient {

    private final RestTemplate restTemplate;
    
    @Value("${data.management.service.url:http://data-management-service:5004}")
    private String dataManagementServiceUrl;

    public DataManagementClient(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    /**
     * Get data type schema from the data-management-service.
     * 
     * @param dataType The data type identifier (e.g., "transactions", "kyc")
     * @return Map containing the schema definition, or null if not found
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> getDataTypeSchema(String dataType) {
        try {
            String url = dataManagementServiceUrl + "/data-types/" + dataType;
            
            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                url,
                HttpMethod.GET,
                new HttpEntity<>(new HttpHeaders()),
                (Class<Map<String, Object>>) (Class<?>) Map.class
            );
            
            if (response.getStatusCode().is2xxSuccessful()) {
                Map<String, Object> dataTypeResponse = response.getBody();
                if (dataTypeResponse != null) {
                    // Extract the schema_definition field
                    Object schemaDef = dataTypeResponse.get("schema_definition");
                    
                    if (schemaDef instanceof Map) {
                        return (Map<String, Object>) schemaDef;
                    }
                }
            }
            
            return null;
        } catch (RestClientException e) {
            // Service unavailable or data type not found
            return null;
        }
    }

    /**
     * Check if a data type exists.
     * 
     * @param dataType The data type identifier
     * @return true if the data type exists, false otherwise
     */
    @SuppressWarnings("unchecked")
    public boolean dataTypeExists(String dataType) {
        try {
            String url = dataManagementServiceUrl + "/data-types/" + dataType;
            
            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                url,
                HttpMethod.GET,
                new HttpEntity<>(new HttpHeaders()),
                (Class<Map<String, Object>>) (Class<?>) Map.class
            );
            
            return response.getStatusCode().is2xxSuccessful() && response.getBody() != null;
        } catch (RestClientException e) {
            return false;
        }
    }
}

