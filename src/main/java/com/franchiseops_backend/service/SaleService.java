package com.franchiseops_backend.service;

import com.franchiseops_backend.entity.Outlet;
import com.franchiseops_backend.entity.Sale;
import com.franchiseops_backend.repository.OutletRepository;
import com.franchiseops_backend.repository.SaleRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class SaleService {

    private final SaleRepository saleRepository;
    private final OutletRepository outletRepository;

    public SaleService(
            SaleRepository saleRepository,
            OutletRepository outletRepository) {

        this.saleRepository = saleRepository;
        this.outletRepository = outletRepository;
    }

    public List<Sale> getAllSales() {
        return saleRepository.findAll();
    }

    public Sale getSaleById(Long id) {
        return saleRepository.findById(id)
                .orElseThrow(() ->
                        new RuntimeException("Sale not found with id: " + id));
    }

    public List<Sale> getSalesByOutlet(Long outletId) {
        return saleRepository.findByOutletOutletId(outletId);
    }

    public Sale createSale(Long outletId, Sale sale) {

        Outlet outlet = outletRepository.findById(outletId)
                .orElseThrow(() ->
                        new RuntimeException(
                                "Outlet not found with id: " + outletId));

        sale.setOutlet(outlet);

        return saleRepository.save(sale);
    }

    public Sale updateSale(Long id, Sale updatedSale) {

        Sale existingSale = getSaleById(id);

        existingSale.setSaleDate(
                updatedSale.getSaleDate()
        );

        existingSale.setRevenue(
                updatedSale.getRevenue()
        );

        existingSale.setTransactionCount(
                updatedSale.getTransactionCount()
        );

        return saleRepository.save(existingSale);
    }

    public void deleteSale(Long id) {

        Sale sale = getSaleById(id);

        saleRepository.delete(sale);
    }
}