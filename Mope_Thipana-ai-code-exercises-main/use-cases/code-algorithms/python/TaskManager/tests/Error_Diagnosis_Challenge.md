Error Analysis: **Off-by-One Error**

**Error Description:**
An off-by-one error occurs when a loop runs one time too many or one time too few. In this case, the program attempts to access a list element that is just outside the valid range of indices, resulting in an `IndexError`.

**Root Cause:**
The loop in the `print_inventory_report` function is written as:

```python
for i in range(len(items) + 1):
```

Because Python lists are zero-indexed, a list with `len(items)` elements has valid indices from `0` to `len(items) - 1`. Adding `+ 1` causes the loop to execute one extra iteration, where the code tries to access `items[len(items)]`, which does not exist.

**Solution:**
Update the loop to iterate only over valid indices:

```python
for i in range(len(items)):
    print(f"Item {i+1}: {items[i]['name']} - Quantity: {items[i]['quantity']}")
```

Or use a safer approach that avoids manual index management:

```python
for index, item in enumerate(items, start=1):
    print(f"Item {index}: {item['name']} - Quantity: {item['quantity']}")
```

**Learning Points:**

* Off-by-one errors commonly occur when working with loop boundaries.
* Remember that Python uses zero-based indexing.
* Avoid unnecessary arithmetic in loop ranges when possible.
* Using `enumerate()` or direct iteration makes code safer and easier to read.

