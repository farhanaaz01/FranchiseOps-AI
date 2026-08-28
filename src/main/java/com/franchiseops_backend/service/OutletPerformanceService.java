package com.franchiseops_backend.service;

import com.franchiseops_backend.dto.*;
import com.franchiseops_backend.entity.Outlet;
import com.franchiseops_backend.entity.Sale;
import com.franchiseops_backend.repository.OutletRepository;
import com.franchiseops_backend.repository.SaleRepository;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class OutletPerformanceService {

    private static final BigDecimal UNDERPERFORMANCE_THRESHOLD = new BigDecimal("0.70");
    private static final int HEALTH_SCALE = 2;

    private final OutletRepository outletRepository;
    private final SaleRepository saleRepository;

    public OutletPerformanceService(
            OutletRepository outletRepository,
            SaleRepository saleRepository) {
        this.outletRepository = outletRepository;
        this.saleRepository = saleRepository;
    }

    public OutletPerformanceDTO getOutletPerformance(Long outletId, LocalDate startDate, LocalDate endDate) {
        Outlet outlet = outletRepository.findById(outletId)
                .orElseThrow(() -> new RuntimeException("Outlet not found with id: " + outletId));

        if (startDate == null) {
            startDate = LocalDate.now().minusDays(30);
        }
        if (endDate == null) {
            endDate = LocalDate.now();
        }

        List<Sale> sales = saleRepository.findByOutletOutletIdAndSaleDateBetween(outletId, startDate, endDate);

        BigDecimal totalRevenue = sales.stream()
                .map(Sale::getRevenue)
                .filter(Objects::nonNull)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        Integer totalTransactions = sales.stream()
                .map(Sale::getTransactionCount)
                .filter(Objects::nonNull)
                .mapToInt(Integer::intValue)
                .sum();

        long dayCount = Math.max(1, startDate.datesUntil(endDate.plusDays(1)).count());

        BigDecimal averageRevenuePerDay = totalRevenue.divide(
                BigDecimal.valueOf(dayCount), HEALTH_SCALE, RoundingMode.HALF_UP);

        BigDecimal averageRevenuePerTransaction = totalTransactions > 0
                ? totalRevenue.divide(BigDecimal.valueOf(totalTransactions), HEALTH_SCALE, RoundingMode.HALF_UP)
                : BigDecimal.ZERO;

        BigDecimal healthScore = computeHealthScore(outlet, totalRevenue, totalTransactions, startDate, endDate);
        String performanceLabel = getPerformanceLabel(healthScore);

        List<RevenueTrendDTO> trend = buildRevenueTrend(outletId, startDate, endDate);

        OutletPerformanceDTO dto = new OutletPerformanceDTO();
        dto.setOutletId(outlet.getOutletId());
        dto.setOutletName(outlet.getOutletName());
        dto.setLocation(outlet.getLocation());
        dto.setStatus(outlet.getStatus());
        dto.setFranchiseId(outlet.getFranchise().getFranchiseId());
        dto.setFranchiseName(outlet.getFranchise().getFranchiseName());
        dto.setTotalRevenue(totalRevenue);
        dto.setTotalTransactions(totalTransactions);
        dto.setAverageRevenuePerDay(averageRevenuePerDay);
        dto.setAverageRevenuePerTransaction(averageRevenuePerTransaction);
        dto.setHealthScore(healthScore);
        dto.setPerformanceLabel(performanceLabel);
        dto.setRevenueTrend(trend);

        return dto;
    }

    public List<FranchiseComparisonDTO> compareOutletsInFranchise(Long franchiseId, LocalDate startDate, LocalDate endDate) {
        if (startDate == null) {
            startDate = LocalDate.now().minusDays(30);
        }
        if (endDate == null) {
            endDate = LocalDate.now();
        }

        List<Outlet> outlets = outletRepository.findByFranchiseFranchiseId(franchiseId);
        List<FranchiseComparisonDTO> comparisons = new ArrayList<>();

        for (Outlet outlet : outlets) {
            List<Sale> sales = saleRepository.findByOutletOutletIdAndSaleDateBetween(
                    outlet.getOutletId(), startDate, endDate);

            BigDecimal totalRevenue = sales.stream()
                    .map(Sale::getRevenue)
                    .filter(Objects::nonNull)
                    .reduce(BigDecimal.ZERO, BigDecimal::add);

            Integer totalTransactions = sales.stream()
                    .map(Sale::getTransactionCount)
                    .filter(Objects::nonNull)
                    .mapToInt(Integer::intValue)
                    .sum();

            BigDecimal healthScore = computeHealthScore(outlet, totalRevenue, totalTransactions, startDate, endDate);

            FranchiseComparisonDTO dto = new FranchiseComparisonDTO();
            dto.setOutletId(outlet.getOutletId());
            dto.setOutletName(outlet.getOutletName());
            dto.setLocation(outlet.getLocation());
            dto.setStatus(outlet.getStatus());
            dto.setTotalRevenue(totalRevenue);
            dto.setTotalTransactions(totalTransactions);
            dto.setHealthScore(healthScore);
            dto.setPerformanceLabel(getPerformanceLabel(healthScore));

            comparisons.add(dto);
        }

        comparisons.sort(Comparator.comparing(FranchiseComparisonDTO::getTotalRevenue).reversed());

        for (int i = 0; i < comparisons.size(); i++) {
            comparisons.get(i).setRank(i + 1);
        }

        return comparisons;
    }

    public DashboardSummaryDTO getDashboardSummary(LocalDate startDate, LocalDate endDate) {
        if (startDate == null) {
            startDate = LocalDate.now().minusDays(30);
        }
        if (endDate == null) {
            endDate = LocalDate.now();
        }

        List<Outlet> allOutlets = outletRepository.findAll();
        List<FranchiseComparisonDTO> comparisons = new ArrayList<>();
        BigDecimal totalRevenue = BigDecimal.ZERO;
        Integer totalTransactions = 0;
        BigDecimal scoreSum = BigDecimal.ZERO;
        int activeCount = 0;
        int underperformingCount = 0;

        for (Outlet outlet : allOutlets) {
            List<Sale> sales = saleRepository.findByOutletOutletIdAndSaleDateBetween(
                    outlet.getOutletId(), startDate, endDate);

            BigDecimal outletRevenue = sales.stream()
                    .map(Sale::getRevenue)
                    .filter(Objects::nonNull)
                    .reduce(BigDecimal.ZERO, BigDecimal::add);

            Integer outletTransactions = sales.stream()
                    .map(Sale::getTransactionCount)
                    .filter(Objects::nonNull)
                    .mapToInt(Integer::intValue)
                    .sum();

            BigDecimal healthScore = computeHealthScore(outlet, outletRevenue, outletTransactions, startDate, endDate);

            FranchiseComparisonDTO dto = new FranchiseComparisonDTO();
            dto.setOutletId(outlet.getOutletId());
            dto.setOutletName(outlet.getOutletName());
            dto.setLocation(outlet.getLocation());
            dto.setStatus(outlet.getStatus());
            dto.setTotalRevenue(outletRevenue);
            dto.setTotalTransactions(outletTransactions);
            dto.setHealthScore(healthScore);
            dto.setPerformanceLabel(getPerformanceLabel(healthScore));

            comparisons.add(dto);

            totalRevenue = totalRevenue.add(outletRevenue);
            totalTransactions += outletTransactions;
            scoreSum = scoreSum.add(healthScore);

            if ("Active".equalsIgnoreCase(outlet.getStatus())) {
                activeCount++;
            }
            if (isUnderperforming(outlet, outletRevenue, startDate, endDate)) {
                underperformingCount++;
            }
        }

        comparisons.sort(Comparator.comparing(FranchiseComparisonDTO::getTotalRevenue).reversed());

        BigDecimal averageHealthScore = comparisons.isEmpty()
                ? BigDecimal.ZERO
                : scoreSum.divide(BigDecimal.valueOf(comparisons.size()), HEALTH_SCALE, RoundingMode.HALF_UP);

        FranchiseComparisonDTO top = comparisons.isEmpty() ? null : comparisons.get(0);
        FranchiseComparisonDTO lowest = comparisons.isEmpty() ? null : comparisons.get(comparisons.size() - 1);

        List<FranchiseComparisonDTO> underperformers = comparisons.stream()
                .filter(c -> "Underperforming".equalsIgnoreCase(c.getPerformanceLabel()))
                .limit(5)
                .collect(Collectors.toList());

        DashboardSummaryDTO summary = new DashboardSummaryDTO();
        summary.setTotalOutlets(allOutlets.size());
        summary.setActiveOutlets(activeCount);
        summary.setUnderperformingOutlets(underperformingCount);
        summary.setTotalRevenue(totalRevenue);
        summary.setTotalTransactions(totalTransactions);
        summary.setAverageHealthScore(averageHealthScore);
        summary.setTopPerformingOutlet(top);
        summary.setLowestPerformingOutlet(lowest);
        summary.setRecentUnderperformers(underperformers);

        return summary;
    }

    public List<UnderperformingOutletDTO> getUnderperformingOutlets(LocalDate startDate, LocalDate endDate) {
        if (startDate == null) {
            startDate = LocalDate.now().minusDays(30);
        }
        if (endDate == null) {
            endDate = LocalDate.now();
        }

        List<Outlet> allOutlets = outletRepository.findAll();
        List<UnderperformingOutletDTO> underperformers = new ArrayList<>();

        for (Outlet outlet : allOutlets) {
            List<Sale> sales = saleRepository.findByOutletOutletIdAndSaleDateBetween(
                    outlet.getOutletId(), startDate, endDate);

            BigDecimal totalRevenue = sales.stream()
                    .map(Sale::getRevenue)
                    .filter(Objects::nonNull)
                    .reduce(BigDecimal.ZERO, BigDecimal::add);

            if (isUnderperforming(outlet, totalRevenue, startDate, endDate)) {
                BigDecimal franchiseAverage = computeFranchiseAverageRevenue(
                        outlet.getFranchise().getFranchiseId(), startDate, endDate);

                BigDecimal healthScore = computeHealthScore(outlet, totalRevenue,
                        sales.stream()
                                .map(Sale::getTransactionCount)
                                .filter(Objects::nonNull)
                                .mapToInt(Integer::intValue)
                                .sum(), startDate, endDate);

                UnderperformingOutletDTO dto = new UnderperformingOutletDTO();
                dto.setOutletId(outlet.getOutletId());
                dto.setOutletName(outlet.getOutletName());
                dto.setLocation(outlet.getLocation());
                dto.setFranchiseId(outlet.getFranchise().getFranchiseId());
                dto.setFranchiseName(outlet.getFranchise().getFranchiseName());
                dto.setTotalRevenue(totalRevenue);
                dto.setFranchiseAverageRevenue(franchiseAverage);
                dto.setHealthScore(healthScore);
                dto.setReason("Revenue is below 70% of the franchise average for the selected period.");

                underperformers.add(dto);
            }
        }

        underperformers.sort(Comparator.comparing(UnderperformingOutletDTO::getHealthScore));
        return underperformers;
    }

    private List<RevenueTrendDTO> buildRevenueTrend(Long outletId, LocalDate startDate, LocalDate endDate) {
        List<Object[]> rows = saleRepository.aggregateDailyRevenueByOutlet(outletId, startDate, endDate);
        List<RevenueTrendDTO> trend = new ArrayList<>();

        for (Object[] row : rows) {
            LocalDate date = (LocalDate) row[0];
            BigDecimal revenue = (BigDecimal) row[1];
            Long transactionLong = (Long) row[2];
            Integer transactions = transactionLong != null ? transactionLong.intValue() : 0;

            trend.add(new RevenueTrendDTO(date, revenue != null ? revenue : BigDecimal.ZERO, transactions));
        }

        return trend;
    }

    private BigDecimal computeHealthScore(Outlet outlet, BigDecimal revenue, Integer transactions,
                                         LocalDate startDate, LocalDate endDate) {
        if (revenue == null) {
            revenue = BigDecimal.ZERO;
        }
        if (transactions == null) {
            transactions = 0;
        }

        BigDecimal franchiseAverage = computeFranchiseAverageRevenue(
                outlet.getFranchise().getFranchiseId(), startDate, endDate);

        if (franchiseAverage.compareTo(BigDecimal.ZERO) == 0) {
            return BigDecimal.ZERO;
        }

        BigDecimal revenueRatio = revenue.divide(franchiseAverage, HEALTH_SCALE, RoundingMode.HALF_UP);

        BigDecimal score = revenueRatio.multiply(new BigDecimal("100"));
        score = score.min(new BigDecimal("100"));

        if (!"Active".equalsIgnoreCase(outlet.getStatus())) {
            score = score.multiply(new BigDecimal("0.50")).setScale(HEALTH_SCALE, RoundingMode.HALF_UP);
        }

        return score;
    }

    private boolean isUnderperforming(Outlet outlet, BigDecimal revenue, LocalDate startDate, LocalDate endDate) {
        if (revenue == null) {
            revenue = BigDecimal.ZERO;
        }
        BigDecimal franchiseAverage = computeFranchiseAverageRevenue(
                outlet.getFranchise().getFranchiseId(), startDate, endDate);

        if (franchiseAverage.compareTo(BigDecimal.ZERO) == 0) {
            return false;
        }

        return revenue.compareTo(franchiseAverage.multiply(UNDERPERFORMANCE_THRESHOLD)) < 0;
    }

    private BigDecimal computeFranchiseAverageRevenue(Long franchiseId, LocalDate startDate, LocalDate endDate) {
        List<Outlet> outlets = outletRepository.findByFranchiseFranchiseId(franchiseId);
        if (outlets.isEmpty()) {
            return BigDecimal.ZERO;
        }

        BigDecimal total = BigDecimal.ZERO;
        for (Outlet outlet : outlets) {
            List<Sale> sales = saleRepository.findByOutletOutletIdAndSaleDateBetween(
                    outlet.getOutletId(), startDate, endDate);
            BigDecimal revenue = sales.stream()
                    .map(Sale::getRevenue)
                    .filter(Objects::nonNull)
                    .reduce(BigDecimal.ZERO, BigDecimal::add);
            total = total.add(revenue);
        }

        return total.divide(BigDecimal.valueOf(outlets.size()), HEALTH_SCALE, RoundingMode.HALF_UP);
    }

    private String getPerformanceLabel(BigDecimal healthScore) {
        if (healthScore == null) {
            return "Unknown";
        }
        if (healthScore.compareTo(new BigDecimal("80")) >= 0) {
            return "Excellent";
        } else if (healthScore.compareTo(new BigDecimal("60")) >= 0) {
            return "Good";
        } else if (healthScore.compareTo(new BigDecimal("40")) >= 0) {
            return "Average";
        } else if (healthScore.compareTo(new BigDecimal("20")) >= 0) {
            return "Underperforming";
        } else {
            return "Critical";
        }
    }
}
