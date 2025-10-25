package com.frauddetection.repository;

import com.frauddetection.domain.RuleVersion;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface RuleVersionRepository extends CrudRepository<RuleVersion, UUID> {
    
    // Find all versions for a specific rule
    List<RuleVersion> findByRuleIdOrderByVersionDesc(UUID ruleId);
    
    // Find specific version of a rule
    Optional<RuleVersion> findByRuleIdAndVersion(UUID ruleId, Integer version);
    
    // Find latest version of a rule
    @Query("SELECT * FROM rule_versions WHERE rule_id = :ruleId ORDER BY version DESC LIMIT 1")
    Optional<RuleVersion> findLatestVersionByRuleId(@Param("ruleId") UUID ruleId);
    
    // Count versions for a rule
    @Query("SELECT COUNT(*) FROM rule_versions WHERE rule_id = :ruleId")
    int countVersionsByRuleId(@Param("ruleId") UUID ruleId);
    
    // Find versions by created by
    List<RuleVersion> findByCreatedBy(String createdBy);
    
    // Find versions created after a specific date
    @Query("SELECT * FROM rule_versions WHERE created_at > :afterDate ORDER BY created_at DESC")
    List<RuleVersion> findVersionsCreatedAfter(@Param("afterDate") String afterDate);
}
