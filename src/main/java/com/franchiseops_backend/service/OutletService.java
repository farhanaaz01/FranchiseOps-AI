package com.franchiseops_backend.service;

import com.franchiseops_backend.entity.Franchise;
import com.franchiseops_backend.entity.Outlet;
import com.franchiseops_backend.repository.FranchiseRepository;
import com.franchiseops_backend.repository.OutletRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class OutletService {

    private final OutletRepository outletRepository;
    private final FranchiseRepository franchiseRepository;

    public OutletService(
            OutletRepository outletRepository,
            FranchiseRepository franchiseRepository) {

        this.outletRepository = outletRepository;
        this.franchiseRepository = franchiseRepository;
    }

    public List<Outlet> getAllOutlets() {
        return outletRepository.findAll();
    }

    public Outlet getOutletById(Long id) {
        return outletRepository.findById(id)
                .orElseThrow(() ->
                        new RuntimeException("Outlet not found with id: " + id));
    }

    public List<Outlet> getOutletsByFranchise(Long franchiseId) {
        return outletRepository.findByFranchiseFranchiseId(franchiseId);
    }

    public Outlet createOutlet(Long franchiseId, Outlet outlet) {

        Franchise franchise = franchiseRepository.findById(franchiseId)
                .orElseThrow(() ->
                        new RuntimeException(
                                "Franchise not found with id: " + franchiseId));

        outlet.setFranchise(franchise);

        return outletRepository.save(outlet);
    }

    public Outlet updateOutlet(Long id, Outlet updatedOutlet) {

        Outlet existingOutlet = getOutletById(id);

        existingOutlet.setOutletName(
                updatedOutlet.getOutletName()
        );

        existingOutlet.setLocation(
                updatedOutlet.getLocation()
        );

        existingOutlet.setStatus(
                updatedOutlet.getStatus()
        );

        return outletRepository.save(existingOutlet);
    }

    public void deleteOutlet(Long id) {

        Outlet outlet = getOutletById(id);

        outletRepository.delete(outlet);
    }
}