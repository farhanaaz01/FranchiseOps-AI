package com.franchiseops_backend.repository;

import com.franchiseops_backend.entity.Outlet;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface OutletRepository extends JpaRepository<Outlet, Long> {

    List<Outlet> findByFranchiseFranchiseId(Long franchiseId);

    List<Outlet> findByFranchiseFranchiseIdAndStatus(Long franchiseId, String status);

    @Query("SELECT COUNT(o) FROM Outlet o WHERE o.franchise.franchiseId = :franchiseId")
    Long countByFranchiseFranchiseId(@Param("franchiseId") Long franchiseId);

    @Query("SELECT COUNT(o) FROM Outlet o WHERE o.franchise.franchiseId = :franchiseId AND o.status = :status")
    Long countByFranchiseFranchiseIdAndStatus(
            @Param("franchiseId") Long franchiseId,
            @Param("status") String status
    );

    @Query("SELECT o FROM Outlet o WHERE o.status = :status")
    List<Outlet> findByStatus(@Param("status") String status);
}
