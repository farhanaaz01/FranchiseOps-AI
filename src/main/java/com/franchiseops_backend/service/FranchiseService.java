package com.franchiseops_backend.service;

import com.franchiseops_backend.entity.Franchise;
import com.franchiseops_backend.repository.FranchiseRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class FranchiseService {

    private final FranchiseRepository franchiseRepository;

    public FranchiseService(FranchiseRepository franchiseRepository) {
        this.franchiseRepository = franchiseRepository;
    }

    public List<Franchise> getAllFranchises() {
        return franchiseRepository.findAll();
    }

    public Franchise getFranchiseById(Long id) {
        return franchiseRepository.findById(id)
                .orElseThrow(() ->
                        new RuntimeException("Franchise not found with id: " + id));
    }

    public Franchise createFranchise(Franchise franchise) {
        return franchiseRepository.save(franchise);
    }

    public Franchise updateFranchise(Long id, Franchise updatedFranchise) {

        Franchise existingFranchise = getFranchiseById(id);

        existingFranchise.setFranchiseName(
                updatedFranchise.getFranchiseName()
        );

        existingFranchise.setRegion(
                updatedFranchise.getRegion()
        );

        existingFranchise.setOwnerName(
                updatedFranchise.getOwnerName()
        );

        return franchiseRepository.save(existingFranchise);
    }

    public void deleteFranchise(Long id) {

        Franchise franchise = getFranchiseById(id);

        franchiseRepository.delete(franchise);
    }
}