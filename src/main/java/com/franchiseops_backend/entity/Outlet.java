package com.franchiseops_backend.entity;


import jakarta.persistence.*;

@Entity
@Table(name = "outlets")
public class Outlet {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "outlet_id")
    private Long outletId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "franchise_id", nullable = false)
    private Franchise franchise;

    @Column(name = "outlet_name", nullable = false)
    private String outletName;

    private String location;

    private String status;

    public Outlet() {
    }

    public Outlet(Franchise franchise, String outletName,
                  String location, String status) {
        this.franchise = franchise;
        this.outletName = outletName;
        this.location = location;
        this.status = status;
    }

    public Long getOutletId() {
        return outletId;
    }

    public void setOutletId(Long outletId) {
        this.outletId = outletId;
    }

    public Franchise getFranchise() {
        return franchise;
    }

    public void setFranchise(Franchise franchise) {
        this.franchise = franchise;
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
}
