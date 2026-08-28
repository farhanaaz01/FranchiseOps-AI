package com.franchiseops_backend.dto;

import java.math.BigDecimal;

public class FranchiseComparisonDTO {

    private Long outletId;
    private String outletName;
    private String location;
    private String status;
    private BigDecimal totalRevenue;
    private Integer totalTransactions;
    private BigDecimal healthScore;
    private Integer rank;
    private String performanceLabel;

    public FranchiseComparisonDTO() {
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

    public BigDecimal getHealthScore() {
        return healthScore;
    }

    public void setHealthScore(BigDecimal healthScore) {
        this.healthScore = healthScore;
    }

    public Integer getRank() {
        return rank;
    }

    public void setRank(Integer rank) {
        this.rank = rank;
    }

    public String getPerformanceLabel() {
        return performanceLabel;
    }

    public void setPerformanceLabel(String performanceLabel) {
        this.performanceLabel = performanceLabel;
    }
}
