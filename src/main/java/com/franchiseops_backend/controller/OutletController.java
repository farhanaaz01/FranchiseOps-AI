package com.franchiseops_backend.controller;

import com.franchiseops_backend.entity.Outlet;
import com.franchiseops_backend.service.OutletService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/outlets")
@CrossOrigin(origins = "http://localhost:5173")
public class OutletController {

    private final OutletService outletService;

    public OutletController(OutletService outletService) {
        this.outletService = outletService;
    }

    // GET all outlets
    @GetMapping
    public ResponseEntity<List<Outlet>> getAllOutlets() {
        return ResponseEntity.ok(
                outletService.getAllOutlets()
        );
    }

    // GET outlet by ID
    @GetMapping("/{id}")
    public ResponseEntity<Outlet> getOutletById(
            @PathVariable Long id) {

        return ResponseEntity.ok(
                outletService.getOutletById(id)
        );
    }

    // GET outlets belonging to a franchise
    @GetMapping("/franchise/{franchiseId}")
    public ResponseEntity<List<Outlet>> getOutletsByFranchise(
            @PathVariable Long franchiseId) {

        return ResponseEntity.ok(
                outletService.getOutletsByFranchise(franchiseId)
        );
    }

    // CREATE outlet
    @PostMapping
    public ResponseEntity<Outlet> createOutlet(
            @RequestParam Long franchiseId,
            @RequestBody Outlet outlet) {

        Outlet created =
                outletService.createOutlet(franchiseId, outlet);

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(created);
    }

    // UPDATE outlet
    @PutMapping("/{id}")
    public ResponseEntity<Outlet> updateOutlet(
            @PathVariable Long id,
            @RequestBody Outlet outlet) {

        return ResponseEntity.ok(
                outletService.updateOutlet(id, outlet)
        );
    }

    // DELETE outlet
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteOutlet(
            @PathVariable Long id) {

        outletService.deleteOutlet(id);

        return ResponseEntity.noContent().build();
    }
}