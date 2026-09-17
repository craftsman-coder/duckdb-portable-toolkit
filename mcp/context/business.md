# Business Context

## Overview
This database contains sales data for a retail company operating in Iran.
All monetary values are in Iranian Rials (IRR) unless otherwise noted.

## Tables

### sales
- Records every sales transaction
- `sale_date`: transaction date (Gregorian, converted from Jalali)
- `amount`: total sale amount in IRR
- `quantity`: number of items sold
- `customer_id`: references customers.id
- `status`: one of 'active', 'cancelled', 'refund'

### customers
- Customer master data
- `customer_id`: primary key
- `segment`: one of 'retail', 'wholesale', 'vip'
- `city`: customer city

## Business Rules
- Only `status = 'active'` records should be included in revenue calculations.
- Sales amounts already include VAT.
- Refunds are recorded as negative amounts.

## Common Metrics
- Total revenue = SUM(amount) WHERE status = 'active'
- Average order value = Total revenue / COUNT(DISTINCT order_id)
- Customer lifetime value = SUM(amount) per customer