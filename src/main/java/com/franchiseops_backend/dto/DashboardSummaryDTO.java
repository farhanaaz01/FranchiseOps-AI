package com.franchiseops_backend.dto;

import java.math.BigDecimal;
import java.util.List;

public class DashboardSummaryDTO {

    private Integer totalOutlets;
    private Integer activeOutlets;
    private Integer underperformingOutlets;
    private BigDecimal totalRevenue;
    private Integer totalTransactions;
    private BigDecimal averageHealthScore;
    private FranchiseComparisonDTO topPerformingOutlet;
    private FranchiseComparisonDTO lowestPerformingOutlet;
    private List<FranchiseComparisonDTO> recentUnderperformers;

    public DashboardSummaryDTO() {
    }

    public Integer getTotalOutlets() {
        return totalOutlets;
    }

    public void setTotalOutlets(Integer totalOutlets) {
        this.totalOutlets = totalOutlets;
    }

    public Integer getActiveOutlets() {
        return activeOutlets;
    }

    public void setActiveOutlets(Integer activeOutlets) {
        this.activeOutlets = activeOutlets;
    }

    public Integer getUnderperformingOutlets() {
        return underperformingOutlets;
    }

    public void setUnderperformingOutlets(Integer underperformingOutlets) {
        this.underperformingOutlets = underperformingOutlets;
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

    public BigDecimal getAverageHealthScore() {
        return averageHealthScore;
    }

    public void setAverageHealthScore(BigDecimal averageHealthScore) {
        this.averageHealthScore = averageHealthScore;
    }

    public FranchiseComparisonDTO getTopPerformingOutlet() {
        return topPerformingOutlet;
    }

    public void setTopPerformingOutlet(FranchiseComparisonDTO topPerformingOutlet) {
        this.topPerformingOutlet = topPerformingOutlet;
    }

    public FranchiseComparisonDTO getLowestPerformingOutlet() {
        return lowestPerformingOutlet;
    }

    public void setLowestPerformingOutlet(FranchiseComparisonDTO lowestPerformingOutlet) {
        this.lowestPerformingOutlet = lowestPerformingOutlet;
    }

    public List<FranchiseComparisonDTO> getRecentUnderperformers() {
        return recentUnderperformers;
    }

    public void setRecentUnderperformers(List<FranchiseComparisonDTO> recentUnderperformers) {
        this.recentUnderperformers = recentUnderperformers;
    }
}
