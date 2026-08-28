package com.franchiseops_backend.entity;


import jakarta.persistence.*;

@Entity
@Table(name = "franchises")
public class Franchise {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "franchise_id")
    private Long franchiseId;

    @Column(name = "franchise_name", nullable = false)
    private String franchiseName;

    private String region;

    @Column(name = "owner_name")
    private String ownerName;

    public Franchise() {
    }

    public Franchise(String franchiseName, String region, String ownerName) {
        this.franchiseName = franchiseName;
        this.region = region;
        this.ownerName = ownerName;
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

    public String getRegion() {
        return region;
    }

    public void setRegion(String region) {
        this.region = region;
    }

    public String getOwnerName() {
        return ownerName;
    }

    public void setOwnerName(String ownerName) {
        this.ownerName = ownerName;
    }
}
