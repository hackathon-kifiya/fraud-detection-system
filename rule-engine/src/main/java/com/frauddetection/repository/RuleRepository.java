package com.frauddetection.repository;

import com.frauddetection.domain.Rule;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface RuleRepository extends CrudRepository<Rule, UUID> {
    
    // Find rules by data type
    List<Rule> findByDataType(Rule.DataType dataType);
    
    // Find rules by status
    List<Rule> findByStatus(Rule.Status status);
    
    // Find rules by data type and status
    List<Rule> findByDataTypeAndStatus(Rule.DataType dataType, Rule.Status status);
    
    // Find active rules by data type
    @Query("SELECT * FROM rules WHERE data_type = :dataType AND status = 'ACTIVE'")
    List<Rule> findActiveRulesByDataType(@Param("dataType") String dataType);
    
    // Find rule by name
    Optional<Rule> findByName(String name);
    
    // Check if rule name exists (excluding current rule)
    @Query("SELECT COUNT(*) > 0 FROM rules WHERE name = :name AND id != :excludeId")
    boolean existsByNameAndIdNot(@Param("name") String name, @Param("excludeId") UUID excludeId);
    
    // Find all rules ordered by created date
    @Query("SELECT * FROM rules ORDER BY created_at DESC")
    List<Rule> findAllOrderByCreatedAt();
    
    // Find rules by created by
    List<Rule> findByCreatedBy(String createdBy);
}
