# Understanding what to change with AI
```python```

## Overview

This document presents a refactored version of the original `process_orders` function. The refactor focuses on:

* Eliminating duplicated validation and error-handling logic
* Separating business rules into small, reusable helper functions
* Improving readability, testability, and maintainability

---

## Helper Functions

### Error Handling

```python
def add_error(error_orders, order_id, message):
    """Append a standardized error entry for an order."""
    error_orders.append({
        'order_id': order_id,
        'error': message
    })
```

---

### Order Validation

```python
def validate_order(order, inventory, customer_data):
    """Validate an order and return an error message if invalid."""
    item_id = order['item_id']
    quantity = order['quantity']
    customer_id = order['customer_id']

    if item_id not in inventory:
        return 'Item not in inventory'

    if inventory[item_id]['quantity'] < quantity:
        return 'Insufficient quantity'

    if customer_id not in customer_data:
        return 'Customer not found'

    return None
```

---

### Pricing and Charges

```python
def calculate_price(item, quantity, customer):
    """Calculate item price, applying premium customer discount if applicable."""
    price = item['price'] * quantity
    if customer['premium']:
        price *= 0.9
    return price


def calculate_shipping(price, customer):
    """Determine shipping cost based on customer location and price."""
    if customer['location'] == 'domestic':
        return 5.99 if price < 50 else 0
    return 15.99


def calculate_tax(price):
    """Calculate tax for a given price."""
    return price * 0.08
```

---

## Refactored `process_orders` Function

```python
def process_orders(orders, inventory, customer_data):
    """Process customer orders and return results, errors, and total revenue."""
    results = []
    error_orders = []
    total_revenue = 0

    for order in orders:
        error = validate_order(order, inventory, customer_data)
        if error:
            add_error(error_orders, order['order_id'], error)
            continue

        item = inventory[order['item_id']]
        customer = customer_data[order['customer_id']]
        quantity = order['quantity']

        price = calculate_price(item, quantity, customer)
        shipping = calculate_shipping(price, customer)
        tax = calculate_tax(price)
        final_price = price + shipping + tax

        # Update inventory and revenue
        item['quantity'] -= quantity
        total_revenue += final_price

        results.append({
            'order_id': order['order_id'],
            'item_id': order['item_id'],
            'quantity': quantity,
            'customer_id': order['customer_id'],
            'price': price,
            'shipping': shipping,
            'tax': tax,
            'final_price': final_price
        })

    return {
        'processed_orders': results,
        'error_orders': error_orders,
        'total_revenue': total_revenue
    }
```

---

## Summary of Improvements

* Validation logic is centralized in `validate_order`
* Error handling is standardized via `add_error`
* Pricing, shipping, and tax logic are isolated into reusable functions
* The main processing loop is easier to read and reason about


### Function Decomposition Challenge

---

## 1. Distinct Responsibilities / Concerns

Although the internal implementation of `generate_sales_report` is not shown, the usage pattern clearly reveals multiple responsibilities:

1. **Input validation**

   * Validate sales data structure
   * Validate parameters (report type, date range, grouping, output format)

2. **Data filtering**

   * Filter sales by date range

3. **Data aggregation / transformation**

   * Summarize totals (revenue, tax, cost, profit)
   * Group data (e.g., by category or region)

4. **Report-type-specific logic**

   * Simple summary report
   * Detailed report
   * Forecast report

5. **Presentation formatting**

   * Convert report to JSON or other formats

6. **Optional features**

   * Chart generation

These concerns are currently coupled through a single entry point.

---

## 2. Suggested Decomposition Strategy

Break the function into **single-responsibility helpers**, each of which can be tested independently:

* `validate_inputs(...)`
* `filter_sales_by_date(...)`
* `generate_summary_report(...)`
* `generate_detailed_report(...)`
* `generate_forecast_report(...)`
* `group_sales_data(...)`
* `calculate_totals(...)`
* `format_output(...)`
* `generate_charts(...)`

The main function becomes an **orchestrator**, not a processor.

---

## 3. Mapping Original Responsibilities to New Functions

| Responsibility       | New Function               |
| -------------------- | -------------------------- |
| Parameter validation | `validate_inputs`          |
| Date filtering       | `filter_sales_by_date`     |
| Summary calculations | `calculate_totals`         |
| Detailed listing     | `generate_detailed_report` |
| Forecast logic       | `generate_forecast_report` |
| Grouping logic       | `group_sales_data`         |
| Chart creation       | `generate_charts`          |
| Output formatting    | `format_output`            |

---

## 4. Refactored Version (Delegating Design)

```python
from typing import List, Dict


def generate_sales_report(
    sales_data: List[Dict],
    report_type: str = 'summary',
    date_range: Dict = None,
    grouping: str = None,
    include_charts: bool = False,
    output_format: str = 'json'
):
    validate_inputs(sales_data, report_type, date_range, grouping)

    filtered_data = filter_sales_by_date(sales_data, date_range)

    if report_type == 'summary':
        report_data = generate_summary_report(filtered_data)
    elif report_type == 'detailed':
        report_data = generate_detailed_report(filtered_data)
    elif report_type == 'forecast':
        report_data = generate_forecast_report(filtered_data, grouping)
    else:
        raise ValueError(f"Unsupported report type: {report_type}")

    if include_charts:
        report_data['charts'] = generate_charts(report_data)

    return format_output(report_data, output_format)


# --- Helper functions ---

def validate_inputs(sales_data, report_type, date_range, grouping):
    if not isinstance(sales_data, list):
        raise ValueError("sales_data must be a list")


def filter_sales_by_date(sales_data, date_range):
    if not date_range:
        return sales_data

    start = date_range['start']
    end = date_range['end']

    return [
        sale for sale in sales_data
        if start <= sale['date'] <= end
    ]


def generate_summary_report(sales_data):
    return calculate_totals(sales_data)


def generate_detailed_report(sales_data):
    totals = calculate_totals(sales_data)
    return {
        'totals': totals,
        'records': sales_data
    }


def generate_forecast_report(sales_data, grouping):
    grouped = group_sales_data(sales_data, grouping)
    return {
        'grouping': grouping,
        'forecast': grouped
    }


def group_sales_data(sales_data, key):
    result = {}
    for sale in sales_data:
        group_key = sale.get(key)
        result.setdefault(group_key, []).append(sale)
    return result


def calculate_totals(sales_data):
    return {
        'revenue': sum(s['amount'] for s in sales_data),
        'tax': sum(s['tax'] for s in sales_data),
        'cost': sum(s['cost'] for s in sales_data),
        'profit': sum(s['amount'] - s['cost'] for s in sales_data)
    }


def generate_charts(report_data):
    return {'charts': 'chart-data-placeholder'}


def format_output(report_data, output_format):
    if output_format == 'json':
        return report_data
    raise ValueError("Unsupported output format")
```

---





