package com.franchiseops_backend.controller;

import com.franchiseops_backend.entity.Sale;
import com.franchiseops_backend.service.SaleService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/sales")
@CrossOrigin(origins = "http://localhost:5173")
public class SaleController {

    private final SaleService saleService;

    public SaleController(SaleService saleService) {
        this.saleService = saleService;
    }

    // GET all sales
    @GetMapping
    public ResponseEntity<List<Sale>> getAllSales() {
        return ResponseEntity.ok(
                saleService.getAllSales()
        );
    }

    // GET sale by ID
    @GetMapping("/{id}")
    public ResponseEntity<Sale> getSaleById(
            @PathVariable Long id) {

        return ResponseEntity.ok(
                saleService.getSaleById(id)
        );
    }

    // GET sales for a particular outlet
    @GetMapping("/outlet/{outletId}")
    public ResponseEntity<List<Sale>> getSalesByOutlet(
            @PathVariable Long outletId) {

        return ResponseEntity.ok(
                saleService.getSalesByOutlet(outletId)
        );
    }

    // CREATE sale
    @PostMapping
    public ResponseEntity<Sale> createSale(
            @RequestParam Long outletId,
            @RequestBody Sale sale) {

        Sale created =
                saleService.createSale(outletId, sale);

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(created);
    }

    // UPDATE sale
    @PutMapping("/{id}")
    public ResponseEntity<Sale> updateSale(
            @PathVariable Long id,
            @RequestBody Sale sale) {

        return ResponseEntity.ok(
                saleService.updateSale(id, sale)
        );
    }

    // DELETE sale
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteSale(
            @PathVariable Long id) {

        saleService.deleteSale(id);

        return ResponseEntity.noContent().build();
    }
}