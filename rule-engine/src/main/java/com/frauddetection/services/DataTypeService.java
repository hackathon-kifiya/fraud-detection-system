package com.frauddetection.services;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.frauddetection.domain.DataType;
import com.frauddetection.dto.DataTypeRequestDto;
import com.frauddetection.dto.DataTypeResponseDto;
import com.frauddetection.exceptions.DataTypeNotFoundException;
import com.frauddetection.exceptions.DuplicateDataTypeException;
import com.frauddetection.exceptions.ValidationException;
import com.frauddetection.mapper.DataTypeMapper;
import com.frauddetection.repository.DataTypeRepository;
import com.frauddetection.repository.RuleRepository;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.IOException;
import java.io.Reader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Instant;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class DataTypeService {

    @Autowired
    private DataTypeRepository dataTypeRepository;
    
    @Autowired
    private RuleRepository ruleRepository;
    
    @Autowired
    private DataTypeMapper dataTypeMapper;
    
    @Autowired
    private ObjectMapper objectMapper;
    
    @Value("${sample.data.directory:../data}")
    private String sampleDataDirectory;

    public DataTypeResponseDto getDataTypeById(UUID id) {
        DataType dataType = dataTypeRepository.findById(id)
                .orElseThrow(() -> new DataTypeNotFoundException("Data type not found with id: " + id));
        return dataTypeMapper.toDtoWithSchema(dataType);
    }
    
    public DataTypeResponseDto getDataTypeByName(String dataType) {
        DataType entity = dataTypeRepository.findByDataType(dataType)
                .orElseThrow(() -> new DataTypeNotFoundException("Data type not found: " + dataType));
        return dataTypeMapper.toDtoWithSchema(entity);
    }

    @Transactional
    public DataTypeResponseDto createDataType(DataTypeRequestDto request) {
        // Check if data type already exists
        if (dataTypeRepository.existsByDataType(request.getDataType())) {
            throw new DuplicateDataTypeException("Data type '" + request.getDataType() + "' already exists");
        }

        // Validate schema structure
        if (request.getSchemaDefinition() != null) {
            validateSchemaDefinition(request.getSchemaDefinition());
        }

        DataType dataType = dataTypeMapper.toEntity(request);
        // Don't set ID - let database generate it with DEFAULT uuid_generate_v4()
        dataType.setCreatedAt(Instant.now());
        dataType.setUpdatedAt(Instant.now());
        
        // Set default status if not provided
        if (dataType.getStatus() == null) {
            dataType.setStatus(DataType.Status.ACTIVE);
        }
        
        DataType saved = dataTypeRepository.save(dataType);
        return dataTypeMapper.toDtoWithSchema(saved);
    }

    public DataType getDataTypeEntity(String dataType) {
        return dataTypeRepository.findByDataType(dataType).orElse(null);
    }

    @Transactional
    public DataTypeResponseDto updateDataType(UUID dataTypeId, DataTypeRequestDto request) {
        // Find existing data type
        DataType dataType = dataTypeRepository.findById(dataTypeId)
                .orElseThrow(() -> new DataTypeNotFoundException("Data type not found with id: " + dataTypeId));

        // Check if data type is being changed and if new name already exists
        if (request.getDataType() != null && !dataType.getDataType().equals(request.getDataType()) 
                && dataTypeRepository.existsByDataTypeAndIdNot(request.getDataType(), dataTypeId)) {
            throw new DuplicateDataTypeException("Data type '" + request.getDataType() + "' already exists");
        }

        // Validate schema if provided
        if (request.getSchemaDefinition() != null) {
            validateSchemaDefinition(request.getSchemaDefinition());
        }

        // Update fields
        if (request.getDataType() != null) {
            dataType.setDataType(request.getDataType());
        }
        if (request.getName() != null) {
            dataType.setName(request.getName());
        }
        if (request.getDescription() != null) {
            dataType.setDescription(request.getDescription());
        }
        if (request.getSchemaDefinition() != null) {
            try {
                dataType.setSchemaDefinition(objectMapper.writeValueAsString(request.getSchemaDefinition()));
            } catch (Exception e) {
                throw new ValidationException("Failed to serialize schema definition", e);
            }
        }
        if (request.getSampleData() != null) {
            try {
                dataType.setSampleData(objectMapper.writeValueAsString(request.getSampleData()));
            } catch (Exception e) {
                throw new ValidationException("Failed to serialize sample data", e);
            }
        }
        
        dataType.setUpdatedAt(Instant.now());
        if (request.getUpdatedBy() != null) {
            dataType.setUpdatedBy(request.getUpdatedBy());
        }
        
        dataType = dataTypeRepository.save(dataType);
        return dataTypeMapper.toDtoWithSchema(dataType);
    }

    @Transactional
    public void deleteDataType(UUID dataTypeId) {
        // Data type deletion is disabled
        throw new ValidationException("Data type deletion is not allowed. Use deactivate instead.");
    }

    @Transactional
    public DataTypeResponseDto activateDataType(UUID dataTypeId) {
        DataType dataType = dataTypeRepository.findById(dataTypeId)
                .orElseThrow(() -> new DataTypeNotFoundException("Data type not found with id: " + dataTypeId));
        dataType.setStatus(DataType.Status.ACTIVE);
        dataType.setUpdatedAt(Instant.now());
        DataType saved = dataTypeRepository.save(dataType);
        return dataTypeMapper.toDtoWithSchema(saved);
    }

    @Transactional
    public DataTypeResponseDto deactivateDataType(UUID dataTypeId) {
        DataType dataType = dataTypeRepository.findById(dataTypeId)
                .orElseThrow(() -> new DataTypeNotFoundException("Data type not found with id: " + dataTypeId));
        dataType.setStatus(DataType.Status.INACTIVE);
        dataType.setUpdatedAt(Instant.now());
        DataType saved = dataTypeRepository.save(dataType);
        return dataTypeMapper.toDtoWithSchema(saved);
    }

    public List<DataTypeResponseDto> getAllDataTypes() {
        return dataTypeRepository.findAllOrderByCreatedAt().stream()
                .map(dataTypeMapper::toDtoWithSchema)
                .collect(Collectors.toList());
    }

    public List<DataTypeResponseDto> getActiveDataTypes() {
        return dataTypeRepository.findByStatus(DataType.Status.ACTIVE).stream()
                .map(dataTypeMapper::toDtoWithSchema)
                .collect(Collectors.toList());
    }

    public List<DataTypeResponseDto> searchDataTypes(String search) {
        return dataTypeRepository.search("%" + search + "%").stream()
                .map(dataTypeMapper::toDtoWithSchema)
                .collect(Collectors.toList());
    }

    /**
     * Validate schema definition structure
     */
    @SuppressWarnings("unchecked")
    private void validateSchemaDefinition(Map<String, Object> schema) {
        if (schema == null || schema.isEmpty()) {
            throw new ValidationException("Schema definition cannot be null or empty");
        }
        
        // Validate fields if present
        if (schema.containsKey("fields")) {
            Object fieldsObj = schema.get("fields");
            if (!(fieldsObj instanceof Map)) {
                throw new ValidationException("Schema 'fields' must be a Map");
            }
            
            Map<String, Object> fields = (Map<String, Object>) fieldsObj;
            if (fields.isEmpty()) {
                throw new ValidationException("Schema must have at least one field");
            }
            
            // Validate field types
            for (Map.Entry<String, Object> entry : fields.entrySet()) {
                if (entry.getValue() == null || entry.getValue().toString().trim().isEmpty()) {
                    throw new ValidationException("Field '" + entry.getKey() + "' must have a type");
                }
            }
            
            // Validate required fields exist in fields list
            if (schema.containsKey("required")) {
                Object requiredObj = schema.get("required");
                if (requiredObj instanceof java.util.List) {
                    java.util.List<?> required = (java.util.List<?>) requiredObj;
                    for (Object reqField : required) {
                        if (!fields.containsKey(reqField.toString())) {
                            throw new ValidationException(
                                "Required field '" + reqField + "' is not defined in fields list"
                            );
                        }
                    }
                }
            }
        }
    }

    /**
     * Get data type schema for validation purposes
     */
    public DataType getDataTypeSchema(String dataType) {
        return dataTypeRepository.findByDataType(dataType)
                .orElse(null);
    }
    
    /**
     * Get sample data from CSV file based on data type
     * 
     * @param dataType the data type name
     * @param limit maximum number of rows to return (default: 10)
     * @return list of records as maps
     */
    public List<Map<String, String>> getSampleDataFromCsv(String dataType, int limit) {
        // Map data type name to CSV file name
        String fileName = mapDataTypeToFileName(dataType);
        Path csvPath = Paths.get(sampleDataDirectory, fileName);
        
        if (!Files.exists(csvPath)) {
            throw new DataTypeNotFoundException("Sample data file not found for data type: " + dataType);
        }
        
        List<Map<String, String>> records = new ArrayList<>();
        
        try (Reader reader = Files.newBufferedReader(csvPath);
             CSVParser csvParser = new CSVParser(reader, CSVFormat.DEFAULT.withFirstRecordAsHeader())) {
            
            // Get header names
            List<String> headers = csvParser.getHeaderNames();
            
            int count = 0;
            for (CSVRecord record : csvParser) {
                if (count >= limit) {
                    break;
                }
                
                Map<String, String> recordMap = new LinkedHashMap<>();
                for (String header : headers) {
                    recordMap.put(header, record.get(header));
                }
                records.add(recordMap);
                count++;
            }
            
        } catch (IOException e) {
            throw new ValidationException("Failed to read sample data file: " + fileName, e);
        }
        
        return records;
    }
    
    /**
     * Maps data type name to CSV file name
     * Converts data type names like "transaction" to file names like "transactions.csv"
     */
    private String mapDataTypeToFileName(String dataType) {
        // Convert data type to file name
        // Examples: "transaction" -> "transactions.csv", "kyc" -> "kyc.csv"
        String fileName = dataType.toLowerCase().replace("_", "");
        
        // Check if file exists with direct name
        Path directPath = Paths.get(sampleDataDirectory, fileName + ".csv");
        if (Files.exists(directPath)) {
            return fileName + ".csv";
        }
        
        // Try plural form
        Path pluralPath = Paths.get(sampleDataDirectory, fileName + "s.csv");
        if (Files.exists(pluralPath)) {
            return fileName + "s.csv";
        }
        
        // Try with different suffix patterns
        String[] suffixes = {"s.csv", "_data.csv", ".csv"};
        for (String suffix : suffixes) {
            Path path = Paths.get(sampleDataDirectory, fileName + suffix);
            if (Files.exists(path)) {
                return path.getFileName().toString();
            }
        }
        
        // Default: return the direct filename
        return fileName + ".csv";
    }
}

