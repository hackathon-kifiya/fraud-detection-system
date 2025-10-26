package com.frauddetection.repository;

import com.frauddetection.domain.DataType;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface DataTypeRepository extends CrudRepository<DataType, UUID> {
    
    Optional<DataType> findByDataType(String dataType);
    
    List<DataType> findByStatus(DataType.Status status);
    
    @Query("SELECT * FROM data_type ORDER BY created_at DESC")
    List<DataType> findAllOrderByCreatedAt();
    
    boolean existsByDataType(String dataType);
    
    @Query("SELECT COUNT(*) > 0 FROM data_type WHERE data_type = :dataType AND id != :excludeId")
    boolean existsByDataTypeAndIdNot(@Param("dataType") String dataType, @Param("excludeId") UUID excludeId);
    
    @Query("SELECT * FROM data_type WHERE data_type ILIKE :search OR name ILIKE :search OR description ILIKE :search ORDER BY created_at DESC")
    List<DataType> search(@Param("search") String search);
}

