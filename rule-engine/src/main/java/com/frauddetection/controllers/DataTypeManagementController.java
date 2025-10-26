package com.frauddetection.controllers;

import com.frauddetection.dto.DataTypeRequestDto;
import com.frauddetection.dto.DataTypeResponseDto;
import com.frauddetection.services.DataTypeService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/data-types")
@Tag(name = "Data Type Management", description = "Manage data type schemas for rule-based fraud detection")
public class DataTypeManagementController {

    @Autowired
    private DataTypeService dataTypeService;

    @Operation(summary = "Create a new data type", description = "Creates a data type schema definition for use in rules")
    @PostMapping
    public ResponseEntity<DataTypeResponseDto> createDataType(@RequestBody DataTypeRequestDto request) {
        DataTypeResponseDto response = dataTypeService.createDataType(request);
        return ResponseEntity.ok(response);
    }

    @Operation(
        summary = "Get all data types",
        description = "Retrieves all data types, optionally filtered by active status or search term"
    )
    @GetMapping
    public ResponseEntity<List<DataTypeResponseDto>> getAllDataTypes(
            @Parameter(description = "Only return active data types") @RequestParam(value = "activeOnly", defaultValue = "false") boolean activeOnly,
            @Parameter(description = "Search term for filtering") @RequestParam(value = "search", required = false) String search) {
        
        List<DataTypeResponseDto> dataTypes;
        
        if (search != null && !search.trim().isEmpty()) {
            dataTypes = dataTypeService.searchDataTypes(search);
        } else if (activeOnly) {
            dataTypes = dataTypeService.getActiveDataTypes();
        } else {
            dataTypes = dataTypeService.getAllDataTypes();
        }
        
        return ResponseEntity.ok(dataTypes);
    }

    @Operation(summary = "Get data type by ID")
    @GetMapping("/{id}")
    public ResponseEntity<DataTypeResponseDto> getDataType(
            @Parameter(description = "Data type UUID") @PathVariable("id") UUID id) {
        DataTypeResponseDto dataType = dataTypeService.getDataTypeById(id);
        return ResponseEntity.ok(dataType);
    }

    @Operation(summary = "Get data type by name")
    @GetMapping("/by-name/{dataType}")
    public ResponseEntity<DataTypeResponseDto> getDataTypeByName(
            @Parameter(description = "Data type name") @PathVariable("dataType") String dataType) {
        DataTypeResponseDto response = dataTypeService.getDataTypeByName(dataType);
        return ResponseEntity.ok(response);
    }

    @Operation(summary = "Update a data type")
    @PutMapping("/{id}")
    public ResponseEntity<DataTypeResponseDto> updateDataType(
            @Parameter(description = "Data type UUID") @PathVariable("id") UUID id,
            @RequestBody DataTypeRequestDto request) {
        DataTypeResponseDto response = dataTypeService.updateDataType(id, request);
        return ResponseEntity.ok(response);
    }

    @Operation(summary = "Delete a data type")
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteDataType(@Parameter(description = "Data type UUID") @PathVariable("id") UUID id) {
        dataTypeService.deleteDataType(id);
        return ResponseEntity.noContent().build();
    }

    @Operation(summary = "Activate a data type")
    @PostMapping("/{id}/activate")
    public ResponseEntity<DataTypeResponseDto> activateDataType(@Parameter(description = "Data type UUID") @PathVariable("id") UUID id) {
        DataTypeResponseDto response = dataTypeService.activateDataType(id);
        return ResponseEntity.ok(response);
    }

    @Operation(summary = "Deactivate a data type")
    @PostMapping("/{id}/deactivate")
    public ResponseEntity<DataTypeResponseDto> deactivateDataType(@Parameter(description = "Data type UUID") @PathVariable("id") UUID id) {
        DataTypeResponseDto response = dataTypeService.deactivateDataType(id);
        return ResponseEntity.ok(response);
    }
    
    @Operation(
        summary = "Get sample data from CSV file",
        description = "Retrieves sample data records from the CSV file associated with the data type"
    )
    @GetMapping("/{dataType}/sample-data")
    public ResponseEntity<?> getSampleData(
            @Parameter(description = "Data type name") @PathVariable("dataType") String dataType,
            @Parameter(description = "Maximum number of records to return") @RequestParam(value = "limit", defaultValue = "10") int limit) {
        try {
            List<java.util.Map<String, String>> sampleData = dataTypeService.getSampleDataFromCsv(dataType, limit);
            return ResponseEntity.ok(sampleData);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(new ErrorResponse(e.getMessage()));
        }
    }
    
    // Simple error response class
    private static class ErrorResponse {
        private String message;
        
        public ErrorResponse(String message) {
            this.message = message;
        }
        
        @SuppressWarnings("unused")
        public String getMessage() {
            return message;
        }
        
        @SuppressWarnings("unused")
        public void setMessage(String message) {
            this.message = message;
        }
    }
}

