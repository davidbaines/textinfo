import numpy as np
from scipy.optimize import linear_sum_assignment

# Define the source and target names
source_names = ['es-RVR95', 'es-NBLA', 'es-BTI', 'es-NVI99', 'es-RVC', 'es-LBLA', 'es-BLP', 'es-PDT', 'es-RV09']
target_names = ['qub-qub', 'quy-RCQ12', 'quz-QC88', 'qvh-qvh', 'qvm-QVMB2', 'qvw-QVW', 'qwh-qwh', 'qxn-qxn', 'qxo-QX0HB', 'qxr-QCA10']

# Your alignment score matrix (convert scores to negative)
cost_matrix = -np.array([
    [0.1756,0.2035,0.2117,0.1728,0.1705,0.1872,0.173,0.1718,0.1719,0.1942],
    [0.1757,0.2024,0.214,0.1728,0.1701,0.1881,0.1727,0.1718,0.1719,0.1882],
    [0.1768,0.1993,0.2096,0.1746,0.1721,0.1874,0.175,0.173,0.1735,0.1789],
    [0.1774,0.1969,0.2066,0.1726,0.1702,0.1876,0.1727,0.1714,0.1714,0.1803],
    [0.1738,0.1946,0.2023,0.1707,0.1679,0.1813,0.1706,0.1697,0.1699,0.1797],
    [0.1705,0.1993,0.2081,0.1683,0.166,0.1817,0.1681,0.1668,0.1672,0.1841],
    [0.173,0.1939,0.2045,0.1706,0.1681,0.1833,0.171,0.1689,0.1694,0.1743],
    [0.172,0.1891,0.1993,0.1705,0.1681,0.1806,0.1707,0.1695,0.1697,0.175],
    [0.1692,0.1961,0.2052,0.1662,0.1639,0.1806,0.1661,0.1643,0.1651,0.1844],
])


# Apply the Hungarian algorithm
row_ind, col_ind = linear_sum_assignment(cost_matrix)

# Resulting optimal alignment
optimal_alignment = cost_matrix[row_ind, col_ind]
total_score = -optimal_alignment.sum()  # Remember to convert back to positive

print("Optimal Assignment:")
for r, c in zip(row_ind, col_ind):
    print(f"Source {source_names[r]} -> Target {target_names[c]}")

print(f"Total Alignment Score: {total_score}")
