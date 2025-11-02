"""
---------------------------------------------------------------
 ALTITUDE-ONLY DRONE CONTROLLER (Webots Educational Example)
---------------------------------------------------------------
Author : Mohamed Elsherbiny
Purpose: Demonstrate how a simple P–D controller regulates altitude.
Robot  : Mavic 2 PRO (Webots simulation)

This example uses:
- GPS sensor for altitude measurement
- Four motors with equal thrust (no roll/pitch control)
- A live plot (Matplotlib) to visualize altitude vs time

---------------------------------------------------------------
"""

# ==============================================================
# 1️⃣ Import required modules
# ==============================================================
from controller import Robot
import math
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt


# ==============================================================
# 2️⃣ Define helper function
# ==============================================================
def clamp(value, min_value, max_value):
    """Keep 'value' within [min_value, max_value]."""
    return max(min_value, min(max_value, value))


# ==============================================================
# 3️⃣ Initialize the robot and its devices
# ==============================================================
robot = Robot()
time_step = int(robot.getBasicTimeStep())

# --- Sensors ---
gps = robot.getDevice("gps")
gps.enable(time_step)     # enable GPS updates every simulation step

# --- Motors ---
# Four propellers (front-left, front-right, rear-left, rear-right)
motors = [
    robot.getDevice("front left propeller"),
    robot.getDevice("front right propeller"),
    robot.getDevice("rear left propeller"),
    robot.getDevice("rear right propeller")
]

# Set motors to velocity control mode
for motor in motors:
    motor.setPosition(float('inf'))   # allows continuous rotation
    motor.setVelocity(0.0)            # start at zero speed


# ==============================================================
# 4️⃣ Define control parameters
# ==============================================================
# Target altitude [meters]
TARGET_ALTITUDE = 2.0

# Base thrust: roughly compensates for gravity at hover
BASE_THRUST = 68.5

# P–D controller gains for altitude
KP_ALTITUDE = 10.0    # proportional term → affects speed of climb
KD_ALTITUDE = 2.0     # derivative term → adds damping (reduces overshoot)

# Variables for storing previous error (for derivative calculation)
previous_error = 0.0


# ==============================================================
# 5️⃣ Prepare live plotting
# ==============================================================
plt.ion()  # interactive mode ON

# Create the figure
fig, ax = plt.subplots(figsize=(8, 4))
ax.set_title("🛸 Altitude Control Demonstration")
ax.set_xlabel("Time [s]")
ax.set_ylabel("Altitude z [m]")
ax.grid(True)

# Two curves: actual altitude & target reference
(line_altitude,) = ax.plot([], [], label="Measured altitude", color='b')
(line_target,) = ax.plot([], [], '--', label="Target altitude", color='r')
ax.legend(loc="upper right")

# Buffers for plotting
time_buffer, altitude_buffer, target_buffer = [], [], []


# ==============================================================
# 6️⃣ Main control loop
# ==============================================================
print("🎬 Starting altitude-only control...")

while robot.step(time_step) != -1:
    # --- 6.1 Read current time and altitude ---
    time_now = robot.getTime()          # simulation time [s]
    altitude = gps.getValues()[2]       # z-coordinate [m]

    # --- 6.2 Compute control error and derivative ---
    error = TARGET_ALTITUDE - altitude
    error_derivative = (error - previous_error) / (time_step / 1000.0)
    previous_error = error

    # --- 6.3 Compute PD control output ---
    control_output = KP_ALTITUDE * error + KD_ALTITUDE * error_derivative

    # --- 6.4 Combine base thrust + control correction ---
    thrust = BASE_THRUST + control_output
    thrust = clamp(thrust, 0.0, 100.0)  # ensure safe limits

    # --- 6.5 Apply equal thrust to all motors ---
    # NOTE: Signs may differ depending on propeller direction
    motors[0].setVelocity( thrust)   # front-left
    motors[1].setVelocity(-thrust)   # front-right
    motors[2].setVelocity(-thrust)   # rear-left
    motors[3].setVelocity( thrust)   # rear-right

    # --- 6.6 Update plot data ---
    time_buffer.append(time_now)
    altitude_buffer.append(altitude)
    target_buffer.append(TARGET_ALTITUDE)

    # --- 6.7 Refresh live plot ---
    line_altitude.set_data(time_buffer, altitude_buffer)
    line_target.set_data(time_buffer, target_buffer)
    ax.relim()
    ax.autoscale_view()
    plt.pause(0.001)

print("✅ Simulation finished. End of demonstration.")