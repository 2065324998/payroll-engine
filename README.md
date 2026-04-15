# Payroll

A payroll calculation engine supporting progressive tax brackets,
overtime with shift differentials, and employee benefits deductions.

## Features

- Federal income tax withholding with progressive brackets
- FICA taxes (Social Security + Medicare) with wage base limits
- Overtime pay (1.5x) with shift differential support
- Employee benefits deductions (health, dental, vision, 401k, HSA)
- Year-to-date tracking across pay periods

## Installation

```bash
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest -v
```
