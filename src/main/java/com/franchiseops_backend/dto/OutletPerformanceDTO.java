package com.franchiseops_backend.dto;

import java.math.BigDecimal;
import java.util.List;

public class OutletPerformanceDTO {

    private Long outletId;
    private String outletName;
    private String location;
    private String status;
    private Long franchiseId;
    private String franchiseName;

    private BigDecimal totalRevenue;
    private Integer totalTransactions;
    private BigDecimal averageRevenuePerDay;
    private BigDecimal averageRevenuePerTransaction;

    private BigDecimal healthScore;
    private String performanceLabel;
    private List<RevenueTrendDTO> revenueTrend;

    public OutletPerformanceDTO() {
    }

    public Long getOutletId() {
        return outletId;
    }

    public void setOutletId(Long outletId) {
        this.outletId = outletId;
    }

    public String getOutletName() {
        return outletName;
    }

    public void setOutletName(String outletName) {
        this.outletName = outletName;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Long getFranchiseId() {
        return franchiseId;
    }

    public void setFranchiseId(Long franchiseId) {
        this.franchiseId = franchiseId;
    }

    public String getFranchiseName() {
        return franchiseName;
    }

    public void setFranchiseName(String franchiseName) {
        this.franchiseName = franchiseName;
    }

    public BigDecimal getTotalRevenue() {
        return totalRevenue;
    }

    public void setTotalRevenue(BigDecimal totalRevenue) {
        this.totalRevenue = totalRevenue;
    }

    public Integer getTotalTransactions() {
        return totalTransactions;
    }

    public void setTotalTransactions(Integer totalTransactions) {
        this.totalTransactions = totalTransactions;
    }

    public BigDecimal getAverageRevenuePerDay() {
        return averageRevenuePerDay;
    }

    public void setAverageRevenuePerDay(BigDecimal averageRevenuePerDay) {
        this.averageRevenuePerDay = averageRevenuePerDay;
    }

    public BigDecimal getAverageRevenuePerTransaction() {
        return averageRevenuePerTransaction;
    }

    public void setAverageRevenuePerTransaction(BigDecimal averageRevenuePerTransaction) {
        this.averageRevenuePerTransaction = averageRevenuePerTransaction;
    }

    public BigDecimal getHealthScore() {
        return healthScore;
    }

    public void setHealthScore(BigDecimal healthScore) {
        this.healthScore = healthScore;
    }

    public String getPerformanceLabel() {
        return performanceLabel;
    }

    public void setPerformanceLabel(String performanceLabel) {
        this.performanceLabel = performanceLabel;
    }

    public List<RevenueTrendDTO> getRevenueTrend() {
        return revenueTrend;
    }

    public void setRevenueTrend(List<RevenueTrendDTO> revenueTrend) {
        this.revenueTrend = revenueTrend;
    }
}
