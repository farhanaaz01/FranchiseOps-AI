from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Attendance, Employee, Outlet, Sale, Schedule
from app.schemas import (
    EmployeePerformanceDTO,
    OutletWorkforceDTO,
    StaffingAlertDTO,
    WorkforceDashboardDTO,
)


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0.00")
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _get_date_range(days: int = 30) -> tuple[date, date]:
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def _get_performance_label(score: Decimal) -> str:
    if score >= Decimal("90"):
        return "Excellent"
    elif score >= Decimal("75"):
        return "Good"
    elif score >= Decimal("60"):
        return "Average"
    elif score >= Decimal("40"):
        return "Below Average"
    else:
        return "Poor"


def analyze_employee(
    db: Session,
    employee_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> EmployeePerformanceDTO:
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise ValueError(f"Employee not found with id: {employee_id}")

    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=30)

    attendances = (
        db.query(Attendance)
        .filter(
            Attendance.employee_id == employee_id,
            Attendance.attendance_date >= start_date,
            Attendance.attendance_date <= end_date,
        )
        .all()
    )

    total_days = len(attendances)
    present_days = sum(1 for a in attendances if a.status == "PRESENT")
    absent_days = sum(1 for a in attendances if a.status == "ABSENT")
    late_days = sum(1 for a in attendances if a.status == "LATE")
    half_day_days = sum(1 for a in attendances if a.status == "HALF_DAY")

    total_hours = sum(_to_decimal(a.hours_worked) for a in attendances)
    average_hours = (total_hours / Decimal(total_days)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if total_days > 0 else Decimal("0.00")

    attendance_rate = (
        (Decimal(present_days) / Decimal(total_days) * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if total_days > 0
        else Decimal("0.00")
    )

    # Productivity score: 60% attendance + 40% hours (8-hour baseline)
    hours_ratio = min(average_hours / Decimal("8"), Decimal("1"))
    productivity_score = (
        attendance_rate * Decimal("0.60") + hours_ratio * Decimal("100") * Decimal("0.40")
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    outlet_name = employee.outlet.outlet_name if employee.outlet else None

    return EmployeePerformanceDTO(
        employee_id=employee.employee_id,
        full_name=employee.full_name,
        outlet_id=employee.outlet_id,
        outlet_name=outlet_name,
        role=employee.role,
        total_days=total_days,
        present_days=present_days,
        absent_days=absent_days,
        late_days=late_days,
        half_day_days=half_day_days,
        attendance_rate=attendance_rate,
        total_hours_worked=total_hours,
        average_hours_per_day=average_hours,
        productivity_score=productivity_score,
        performance_label=_get_performance_label(productivity_score),
    )


def analyze_outlet_workforce(
    db: Session,
    outlet_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> OutletWorkforceDTO:
    outlet = db.query(Outlet).filter(Outlet.outlet_id == outlet_id).first()
    if not outlet:
        raise ValueError(f"Outlet not found with id: {outlet_id}")

    employees = db.query(Employee).filter(Employee.outlet_id == outlet_id).all()
    performances = [
        analyze_employee(db, employee.employee_id, start_date, end_date)
        for employee in employees
    ]

    active_employees = [e for e in employees if e.status and e.status.upper() == "ACTIVE"]
    total_employees = len(employees)

    if performances:
        avg_attendance = (
            sum(p.attendance_rate for p in performances) / len(performances)
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_hours = sum(p.total_hours_worked for p in performances)
    else:
        avg_attendance = Decimal("0.00")
        total_hours = Decimal("0.00")

    staffing_shortage_count = len(get_staffing_alerts_for_outlet(db, outlet_id))

    return OutletWorkforceDTO(
        outlet_id=outlet_id,
        outlet_name=outlet.outlet_name,
        total_employees=total_employees,
        active_employees=len(active_employees),
        average_attendance_rate=avg_attendance,
        total_hours_worked=total_hours,
        staffing_shortage_count=staffing_shortage_count,
        employee_performances=performances,
    )


def get_staffing_alerts_for_outlet(db: Session, outlet_id: int) -> list[StaffingAlertDTO]:
    alerts = []
    outlet = db.query(Outlet).filter(Outlet.outlet_id == outlet_id).first()
    if not outlet:
        return alerts

    employees = db.query(Employee).filter(Employee.outlet_id == outlet_id).all()
    active_employees = [e for e in employees if e.status and e.status.upper() == "ACTIVE"]

    # Expected staff = max(3, 60% of active employees)
    expected_staff = max(3, int(len(active_employees) * 0.6))

    today = date.today()
    for day_offset in range(7):
        check_date = today + timedelta(days=day_offset)
        scheduled_count = (
            db.query(Schedule)
            .filter(
                Schedule.schedule_date == check_date,
                Schedule.employee_id.in_([e.employee_id for e in active_employees]),
                Schedule.status == "SCHEDULED",
            )
            .count()
        )

        if scheduled_count < expected_staff:
            alerts.append(
                StaffingAlertDTO(
                    outlet_id=outlet_id,
                    outlet_name=outlet.outlet_name,
                    alert_type="SHORTAGE",
                    scheduled_staff_count=scheduled_count,
                    expected_staff_count=expected_staff,
                    message=f"Only {scheduled_count} staff scheduled on {check_date}; expected {expected_staff}",
                )
            )
        elif scheduled_count > expected_staff * 2:
            alerts.append(
                StaffingAlertDTO(
                    outlet_id=outlet_id,
                    outlet_name=outlet.outlet_name,
                    alert_type="OVERSTAFFED",
                    scheduled_staff_count=scheduled_count,
                    expected_staff_count=expected_staff,
                    message=f"{scheduled_count} staff scheduled on {check_date}; more than expected {expected_staff}",
                )
            )

    return alerts


def get_all_staffing_alerts(db: Session) -> list[StaffingAlertDTO]:
    alerts = []
    outlets = db.query(Outlet).all()
    for outlet in outlets:
        alerts.extend(get_staffing_alerts_for_outlet(db, outlet.outlet_id))
    return alerts


def get_workforce_dashboard(db: Session) -> WorkforceDashboardDTO:
    employees = db.query(Employee).all()
    active_employees = [e for e in employees if e.status and e.status.upper() == "ACTIVE"]

    performances = [analyze_employee(db, e.employee_id) for e in employees]

    if performances:
        avg_attendance = (
            sum(p.attendance_rate for p in performances) / len(performances)
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_hours = sum(p.total_hours_worked for p in performances)
    else:
        avg_attendance = Decimal("0.00")
        total_hours = Decimal("0.00")

    sorted_performances = sorted(performances, key=lambda p: p.productivity_score, reverse=True)
    top_performers = sorted_performances[:5]
    underperformers = sorted([p for p in performances if p.performance_label in ("Poor", "Below Average")], key=lambda p: p.productivity_score)[:5]

    staffing_alerts = get_all_staffing_alerts(db)

    outlets_with_employees = len(set(e.outlet_id for e in employees))

    return WorkforceDashboardDTO(
        total_employees=len(employees),
        active_employees=len(active_employees),
        total_outlets_with_employees=outlets_with_employees,
        average_attendance_rate=avg_attendance,
        total_hours_worked=total_hours,
        top_performers=top_performers,
        underperformers=underperformers,
        staffing_alerts=staffing_alerts[:10],
    )
