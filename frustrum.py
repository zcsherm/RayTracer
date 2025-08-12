import numpy as np

# Define the direction vectors
d1 = np.array([0.720, 0.643, 0.262])
d2 = np.array([0.720, -0.643, 0.262])
d3 = np.array([-0.720, -0.643, 0.262])
d4 = np.array([-0.720, 0.643, 0.262])

# Normalize the vectors
d1_norm = d1 / np.linalg.norm(d1)
d2_norm = d2 / np.linalg.norm(d2)
d3_norm = d3 / np.linalg.norm(d3)
d4_norm = d4 / np.linalg.norm(d4)

# Calculate angles between opposite vectors (Horizontal FOV and Vertical FOV)
angle_horizontal = np.arccos(np.clip(np.dot(d1_norm, d3_norm), -1.0, 1.0))  # d1 and d3
angle_vertical = np.arccos(np.clip(np.dot(d2_norm, d4_norm), -1.0, 1.0))  # d2 and d4

# Convert to degrees
fov_horizontal = np.degrees(angle_horizontal)
fov_vertical = np.degrees(angle_vertical)

print(f"Horizontal FOV: {fov_horizontal:.2f} degrees")
print(f"Vertical FOV: {fov_vertical:.2f} degrees")