package com.franchiseops_backend.dto;

import java.math.BigDecimal;

public class UnderperformingOutletDTO {

    private Long outletId;
    private String outletName;
    private String location;
    private Long franchiseId;
    private String franchiseName;
    private BigDecimal totalRevenue;
    private BigDecimal franchiseAverageRevenue;
    private BigDecimal healthScore;
    private String reason;

    public UnderperformingOutletDTO() {
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

    public BigDecimal getFranchiseAverageRevenue() {
        return franchiseAverageRevenue;
    }

    public void setFranchiseAverageRevenue(BigDecimal franchiseAverageRevenue) {
        this.franchiseAverageRevenue = franchiseAverageRevenue;
    }

    public BigDecimal getHealthScore() {
        return healthScore;
    }

    public void setHealthScore(BigDecimal healthScore) {
        this.healthScore = healthScore;
    }

    public String getReason() {
        return reason;
    }

    public void setReason(String reason) {
        this.reason = reason;
    }
}
