package com.franchiseops_backend.controller;

import com.franchiseops_backend.dto.DashboardSummaryDTO;
import com.franchiseops_backend.dto.FranchiseComparisonDTO;
import com.franchiseops_backend.dto.OutletPerformanceDTO;
import com.franchiseops_backend.dto.UnderperformingOutletDTO;
import com.franchiseops_backend.service.OutletPerformanceService;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/dashboard")
@CrossOrigin(origins = "http://localhost:5173")
public class DashboardController {

    private final OutletPerformanceService outletPerformanceService;

    public DashboardController(OutletPerformanceService outletPerformanceService) {
        this.outletPerformanceService = outletPerformanceService;
    }

    @GetMapping("/outlets/{outletId}")
    public ResponseEntity<OutletPerformanceDTO> getOutletPerformance(
            @PathVariable Long outletId,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {

        return ResponseEntity.ok(
                outletPerformanceService.getOutletPerformance(outletId, startDate, endDate)
        );
    }

    @GetMapping("/franchises/{franchiseId}/compare")
    public ResponseEntity<List<FranchiseComparisonDTO>> compareFranchiseOutlets(
            @PathVariable Long franchiseId,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {

        return ResponseEntity.ok(
                outletPerformanceService.compareOutletsInFranchise(franchiseId, startDate, endDate)
        );
    }

    @GetMapping("/summary")
    public ResponseEntity<DashboardSummaryDTO> getDashboardSummary(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {

        return ResponseEntity.ok(
                outletPerformanceService.getDashboardSummary(startDate, endDate)
        );
    }

    @GetMapping("/underperforming")
    public ResponseEntity<List<UnderperformingOutletDTO>> getUnderperformingOutlets(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {

        return ResponseEntity.ok(
                outletPerformanceService.getUnderperformingOutlets(startDate, endDate)
        );
    }
}
