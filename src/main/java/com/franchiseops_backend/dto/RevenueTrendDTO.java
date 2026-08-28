package com.franchiseops_backend.dto;

import java.math.BigDecimal;
import java.time.LocalDate;

public class RevenueTrendDTO {

    private LocalDate date;
    private BigDecimal revenue;
    private Integer transactions;

    public RevenueTrendDTO() {
    }

    public RevenueTrendDTO(LocalDate date, BigDecimal revenue, Integer transactions) {
        this.date = date;
        this.revenue = revenue;
        this.transactions = transactions;
    }

    public LocalDate getDate() {
        return date;
    }

    public void setDate(LocalDate date) {
        this.date = date;
    }

    public BigDecimal getRevenue() {
        return revenue;
    }

    public void setRevenue(BigDecimal revenue) {
        this.revenue = revenue;
    }

    public Integer getTransactions() {
        return transactions;
    }

    public void setTransactions(Integer transactions) {
        this.transactions = transactions;
    }
}
