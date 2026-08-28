package com.franchiseops_backend.config;

import com.franchiseops_backend.entity.Franchise;
import com.franchiseops_backend.entity.Outlet;
import com.franchiseops_backend.entity.Sale;
import com.franchiseops_backend.repository.FranchiseRepository;
import com.franchiseops_backend.repository.OutletRepository;
import com.franchiseops_backend.repository.SaleRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.util.Random;

@Configuration
public class DataSeeder {

    @Bean
    CommandLineRunner seedData(
            FranchiseRepository franchiseRepository,
            OutletRepository outletRepository,
            SaleRepository saleRepository) {

        return args -> {
            if (franchiseRepository.count() > 0) {
                return;
            }

            Franchise burgerKing = franchiseRepository.save(
                    new Franchise("Burger King North", "North Region", "Alice Johnson")
            );

            Franchise subway = franchiseRepository.save(
                    new Franchise("Subway South", "South Region", "Bob Smith")
            );

            Outlet outlet1 = outletRepository.save(
                    new Outlet(burgerKing, "BK Downtown", "Downtown", "Active")
            );
            Outlet outlet2 = outletRepository.save(
                    new Outlet(burgerKing, "BK Mall", "Mall Road", "Active")
            );
            Outlet outlet3 = outletRepository.save(
                    new Outlet(subway, "Subway City Center", "City Center", "Active")
            );
            Outlet outlet4 = outletRepository.save(
                    new Outlet(subway, "Subway Airport", "Airport", "Inactive")
            );

            seedSales(saleRepository, outlet1, 30, new BigDecimal("1200"), new BigDecimal("300"));
            seedSales(saleRepository, outlet2, 30, new BigDecimal("900"), new BigDecimal("250"));
            seedSales(saleRepository, outlet3, 30, new BigDecimal("1500"), new BigDecimal("400"));
            seedSales(saleRepository, outlet4, 30, new BigDecimal("500"), new BigDecimal("150"));
        };
    }

    private void seedSales(SaleRepository saleRepository, Outlet outlet, int days,
                           BigDecimal baseRevenue, BigDecimal baseTransactions) {
        Random random = new Random(outlet.getOutletId().intValue());
        LocalDate today = LocalDate.now();

        for (int i = 0; i < days; i++) {
            LocalDate saleDate = today.minusDays(days - i);

            double revenueMultiplier = 0.7 + (random.nextDouble() * 0.6);
            BigDecimal revenue = baseRevenue
                    .multiply(BigDecimal.valueOf(revenueMultiplier))
                    .setScale(2, RoundingMode.HALF_UP);

            double transactionMultiplier = 0.7 + (random.nextDouble() * 0.6);
            Integer transactions = baseTransactions
                    .multiply(BigDecimal.valueOf(transactionMultiplier))
                    .intValue();

            saleRepository.save(new Sale(outlet, saleDate, revenue, transactions));
        }
    }
}
