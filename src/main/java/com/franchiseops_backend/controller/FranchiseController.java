package com.franchiseops_backend.controller;

import com.franchiseops_backend.entity.Franchise;
import com.franchiseops_backend.service.FranchiseService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/franchises")
@CrossOrigin(origins = "http://localhost:5173")
public class FranchiseController {

    private final FranchiseService franchiseService;

    public FranchiseController(FranchiseService franchiseService) {
        this.franchiseService = franchiseService;
    }

    // GET all franchises
    @GetMapping
    public ResponseEntity<List<Franchise>> getAllFranchises() {
        return ResponseEntity.ok(
                franchiseService.getAllFranchises()
        );
    }

    // GET franchise by ID
    @GetMapping("/{id}")
    public ResponseEntity<Franchise> getFranchiseById(
            @PathVariable Long id) {

        return ResponseEntity.ok(
                franchiseService.getFranchiseById(id)
        );
    }

    // CREATE franchise
    @PostMapping
    public ResponseEntity<Franchise> createFranchise(
            @RequestBody Franchise franchise) {

        Franchise created =
                franchiseService.createFranchise(franchise);

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(created);
    }

    // UPDATE franchise
    @PutMapping("/{id}")
    public ResponseEntity<Franchise> updateFranchise(
            @PathVariable Long id,
            @RequestBody Franchise franchise) {

        return ResponseEntity.ok(
                franchiseService.updateFranchise(id, franchise)
        );
    }

    // DELETE franchise
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteFranchise(
            @PathVariable Long id) {

        franchiseService.deleteFranchise(id);

        return ResponseEntity.noContent().build();
    }
}