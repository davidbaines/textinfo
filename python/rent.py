
rent1 = 0
rent2 = 0

rentrate1 = 1000
rentrate2 = 1000

for i in range(1,121):
    if i % 12 == 0:
        rentrate1 += 12
    if i % 24 == 0:
        rentrate2 += 25
    rent1 = rent1 + rentrate1
    rent2 = rent2 + rentrate2
    #print(rentrate1, rent1, "\t", rentrate2, rent2)


def calculate_equivalent_annual_increase(initial_rent, biennial_increase, years):
    target_total = 0
    biennial_rent = initial_rent

    # Calculate total rent paid with biennial increase
    for i in range(1, years * 12 + 1):
        if i % 24 == 0:
            biennial_rent = round(biennial_rent + biennial_increase, 2)
        target_total += biennial_rent

    # Binary search to find the equivalent annual increase
    low, high = 0, biennial_increase
    while high - low > 0.01:  # Precision to 2 decimal places
        mid = (low + high) / 2
        annual_total = 0
        annual_rent = initial_rent

        for i in range(1, years * 12 + 1):
            if i % 12 == 0:
                annual_rent = round(annual_rent + mid)
            annual_total += annual_rent

        if annual_total < target_total:
            low = mid
        else:
            high = mid

    return round(low, 2)

# Original rent calculation
rent1 = 0
rent2 = 0
rentrate1 = 1000
rentrate2 = 1000

for i in range(1, 121):
    if i % 12 == 0:
        rentrate1 = round(rentrate1 + 12, 2)
    if i % 24 == 0:
        rentrate2 += 25
    rent1 = rent1 + rentrate1
    rent2 = rent2 + rentrate2
    print(rentrate1, rent1, "\t", rentrate2, rent2)

# Calculate equivalent annual increase
years = 10
equivalent_annual_increase = calculate_equivalent_annual_increase(1000, 25, years)
print(f"\nEquivalent annual increase: £{equivalent_annual_increase}")

# Verify the result
rent_annual = 0
rent_biennial = 0
rate_annual = 1000
rate_biennial = 1000

for i in range(1, years * 12 + 1):
    if i % 12 == 0:
        rate_annual += equivalent_annual_increase
    if i % 24 == 0:
        rate_biennial += 25
    rent_annual += rate_annual
    rent_biennial += rate_biennial

print(f"Total rent paid with £25 biennial increase: £{rent_biennial}")
print(f"Total rent paid with £{equivalent_annual_increase} annual increase: £{rent_annual}")
if rent_annual > rent_biennial:
    print(f"Total rent paid with annual increase of £{equivalent_annual_increase} is £{rent_annual - rent_biennial} more.")
elif rent_biennial > rent_annual:
    print(f"Total rent paid with biennial increase of £25 is £{rent_biennial - rent_annual} more.")
else:
    print(f"Total rent paid is the same.")