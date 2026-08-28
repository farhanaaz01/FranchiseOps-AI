package com.franchiseops_backend.repository;

import com.franchiseops_backend.entity.Sale;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

public interface SaleRepository extends JpaRepository<Sale, Long> {

    List<Sale> findByOutletOutletId(Long outletId);

    List<Sale> findByOutletOutletIdAndSaleDateBetween(
            Long outletId,
            LocalDate startDate,
            LocalDate endDate
    );

    @Query("SELECT s.outlet.outletId, SUM(s.revenue), SUM(s.transactionCount) " +
           "FROM Sale s " +
           "WHERE s.saleDate BETWEEN :startDate AND :endDate " +
           "GROUP BY s.outlet.outletId")
    List<Object[]> aggregateRevenueByOutlet(
            @Param("startDate") LocalDate startDate,
            @Param("endDate") LocalDate endDate
    );

    @Query("SELECT s.saleDate, SUM(s.revenue), SUM(s.transactionCount) " +
           "FROM Sale s " +
           "WHERE s.outlet.outletId = :outletId " +
           "AND s.saleDate BETWEEN :startDate AND :endDate " +
           "GROUP BY s.saleDate " +
           "ORDER BY s.saleDate")
    List<Object[]> aggregateDailyRevenueByOutlet(
            @Param("outletId") Long outletId,
            @Param("startDate") LocalDate startDate,
            @Param("endDate") LocalDate endDate
    );

    @Query("SELECT SUM(s.revenue) FROM Sale s " +
           "WHERE s.outlet.outletId = :outletId " +
           "AND s.saleDate BETWEEN :startDate AND :endDate")
    BigDecimal sumRevenueByOutletAndDateRange(
            @Param("outletId") Long outletId,
            @Param("startDate") LocalDate startDate,
            @Param("endDate") LocalDate endDate
    );

    @Query("SELECT SUM(s.revenue) FROM Sale s " +
           "WHERE s.outlet.franchise.franchiseId = :franchiseId " +
           "AND s.saleDate BETWEEN :startDate AND :endDate")
    BigDecimal sumRevenueByFranchiseAndDateRange(
            @Param("franchiseId") Long franchiseId,
            @Param("startDate") LocalDate startDate,
            @Param("endDate") LocalDate endDate
    );

    @Query("SELECT s.outlet.outletId, SUM(s.revenue) " +
           "FROM Sale s " +
           "WHERE s.outlet.franchise.franchiseId = :franchiseId " +
           "AND s.saleDate BETWEEN :startDate AND :endDate " +
           "GROUP BY s.outlet.outletId")
    List<Object[]> sumRevenueByOutletsInFranchise(
            @Param("franchiseId") Long franchiseId,
            @Param("startDate") LocalDate startDate,
            @Param("endDate") LocalDate endDate
    );

    @Query("SELECT COUNT(s) > 0 FROM Sale s WHERE s.outlet.outletId = :outletId")
    boolean existsByOutletOutletId(@Param("outletId") Long outletId);
}
