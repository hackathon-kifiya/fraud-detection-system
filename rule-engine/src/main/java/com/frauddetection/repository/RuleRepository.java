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
    
    List<Rule> findByDataType(String dataType);
    
    List<Rule> findByStatus(Rule.Status status);
    
    List<Rule> findByDataTypeAndStatus(String dataType, Rule.Status status);
    
    @Query("SELECT * FROM rule WHERE data_type = :dataType AND status = 'ACTIVE'")
    List<Rule> findActiveRulesByDataType(@Param("dataType") String dataType);
    
    Optional<Rule> findByName(String name);
    
    @Query("SELECT COUNT(*) > 0 FROM rule WHERE name = :name AND id != :excludeId")
    boolean existsByNameAndIdNot(@Param("name") String name, @Param("excludeId") UUID excludeId);
    
    @Query("SELECT * FROM rule ORDER BY created_at DESC")
    List<Rule> findAllOrderByCreatedAt();
    
    List<Rule> findByCreatedBy(String createdBy);
    
    @Query("SELECT * FROM rule WHERE (name ILIKE :search OR description ILIKE :search) ORDER BY created_at DESC")
    List<Rule> findByNameOrDescriptionContainingIgnoreCase(@Param("search") String search);
    
    @Query("SELECT * FROM rule WHERE (name ILIKE :search OR description ILIKE :search) AND data_type = :dataType ORDER BY created_at DESC")
    List<Rule> findByNameOrDescriptionContainingIgnoreCaseAndDataType(@Param("search") String search, @Param("dataType") String dataType);
    
    @Query("SELECT * FROM rule WHERE (name ILIKE :search OR description ILIKE :search) AND status = :status ORDER BY created_at DESC")
    List<Rule> findByNameOrDescriptionContainingIgnoreCaseAndStatus(@Param("search") String search, @Param("status") String status);
    
    @Query("SELECT * FROM rule WHERE (name ILIKE :search OR description ILIKE :search) AND data_type = :dataType AND status = :status ORDER BY created_at DESC")
    List<Rule> findByNameOrDescriptionContainingIgnoreCaseAndDataTypeAndStatus(@Param("search") String search, @Param("dataType") String dataType, @Param("status") String status);
    
    @Query("SELECT * FROM rule ORDER BY created_at DESC LIMIT :limit OFFSET :offset")
    List<Rule> findAllOrderByCreatedAtWithPagination(@Param("limit") int limit, @Param("offset") int offset);
    
    @Query("SELECT * FROM rule WHERE data_type = :dataType ORDER BY created_at DESC LIMIT :limit OFFSET :offset")
    List<Rule> findByDataTypeWithPagination(@Param("dataType") String dataType, @Param("limit") int limit, @Param("offset") int offset);
    
    @Query("SELECT * FROM rule WHERE status = :status ORDER BY created_at DESC LIMIT :limit OFFSET :offset")
    List<Rule> findByStatusWithPagination(@Param("status") String status, @Param("limit") int limit, @Param("offset") int offset);
    
    @Query("SELECT * FROM rule WHERE data_type = :dataType AND status = :status ORDER BY created_at DESC LIMIT :limit OFFSET :offset")
    List<Rule> findByDataTypeAndStatusWithPagination(@Param("dataType") String dataType, @Param("status") String status, @Param("limit") int limit, @Param("offset") int offset);
    
    @Query("SELECT * FROM rule WHERE (name ILIKE :search OR description ILIKE :search) ORDER BY created_at DESC LIMIT :limit OFFSET :offset")
    List<Rule> findByNameOrDescriptionContainingIgnoreCaseWithPagination(@Param("search") String search, @Param("limit") int limit, @Param("offset") int offset);
    
    @Query("SELECT * FROM rule WHERE (name ILIKE :search OR description ILIKE :search) AND data_type = :dataType ORDER BY created_at DESC LIMIT :limit OFFSET :offset")
    List<Rule> findByNameOrDescriptionContainingIgnoreCaseAndDataTypeWithPagination(@Param("search") String search, @Param("dataType") String dataType, @Param("limit") int limit, @Param("offset") int offset);
    
    @Query("SELECT * FROM rule WHERE (name ILIKE :search OR description ILIKE :search) AND status = :status ORDER BY created_at DESC LIMIT :limit OFFSET :offset")
    List<Rule> findByNameOrDescriptionContainingIgnoreCaseAndStatusWithPagination(@Param("search") String search, @Param("status") String status, @Param("limit") int limit, @Param("offset") int offset);
    
    @Query("SELECT * FROM rule WHERE (name ILIKE :search OR description ILIKE :search) AND data_type = :dataType AND status = :status ORDER BY created_at DESC LIMIT :limit OFFSET :offset")
    List<Rule> findByNameOrDescriptionContainingIgnoreCaseAndDataTypeAndStatusWithPagination(@Param("search") String search, @Param("dataType") String dataType, @Param("status") String status, @Param("limit") int limit, @Param("offset") int offset);
}
