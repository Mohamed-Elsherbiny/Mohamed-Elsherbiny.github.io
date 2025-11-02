"""
=====================================================================
 ALTITUDE + ATTITUDE DRONE CONTROLLER — EDUCATIONAL VERSION
=====================================================================
Author : Mohamed Elsherbiny
Purpose: Demonstrate PD feedback control for both altitude and attitude.
Robot  : Mavic 2 PRO (Webots)
Sensors: IMU, Gyroscope, GPS
Actuators: 4 propellers in velocity mode
Visualization: Live Matplotlib plots (no files saved)
=====================================================================
"""

# ----------------------------------------------------------
# 1️⃣ Imports
# ----------------------------------------------------------
from controller import Robot
import math
import matplotlib
matplotlib.use("TkAgg")        # GUI backend for live plots
import matplotlib.pyplot as plt


# ----------------------------------------------------------
# 2️⃣ Helper function
# ----------------------------------------------------------
def clamp(value, lo, hi):
    """Keep 'value' within [lo, hi] to avoid unsafe motor commands."""
    return max(lo, min(hi, value))


# ----------------------------------------------------------
# 3️⃣ Robot setup and device initialization
# ----------------------------------------------------------
robot = Robot()
dt = int(robot.getBasicTimeStep())  # simulation time step in ms

# --- Sensors ---
imu  = robot.getDevice("inertial unit"); imu.enable(dt)
gyro = robot.getDevice("gyro");         gyro.enable(dt)
gps  = robot.getDevice("gps");          gps.enable(dt)

# --- Motors ---
mFL = robot.getDevice("front left propeller")
mFR = robot.getDevice("front right propeller")
mRL = robot.getDevice("rear left propeller")
mRR = robot.getDevice("rear right propeller")

# Set all propellers to velocity control mode
for m in (mFL, mFR, mRL, mRR):
    m.setPosition(float('inf'))
    m.setVelocity(0.0)


# ----------------------------------------------------------
# 4️⃣ Control parameters
# ----------------------------------------------------------
# --- Base thrust & altitude loop ---
T0 = 68.5            # approximate hover thrust (depends on model weight)
target_alt = 2.0     # desired altitude [m]
Kp_z, Kd_z = 2.0, 0  # altitude PD gains
z_error_prev = 0.0   # for derivative term

# --- Attitude (roll/pitch/yaw) loops ---
Kp_phi, Kd_phi = 40.0, 1.0   # roll
Kp_the, Kd_the = 30.0, 1.0   # pitch
Kd_psi         = 0.4         # yaw-rate damping only

"""
Explanation:
- Kp_z controls how fast altitude errors are corrected.
- Kd_z adds damping (set to 0 here for demonstration).
- Roll (phi) and pitch (theta) PDs stabilize orientation.
- Yaw control uses only D (rate) feedback to prevent spinning.
"""


# ----------------------------------------------------------
# 5️⃣ Live plotting setup
# ----------------------------------------------------------
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

# --- Altitude plot ---
ax1.set_title("Altitude Control")
ax1.set_ylabel("z [m]")
(line_z,)     = ax1.plot([], [], label="Altitude (measured)")
(line_z_ref,) = ax1.plot([], [], "r--", label="Target")
ax1.legend(); ax1.grid(True)

# --- Attitude plot ---
ax2.set_title("Attitude Angles")
ax2.set_xlabel("time [s]")
ax2.set_ylabel("Angle [deg]")
(line_roll,)  = ax2.plot([], [], label="Roll")
(line_pitch,) = ax2.plot([], [], label="Pitch")
(line_yaw,)   = ax2.plot([], [], label="Yaw")
ax2.legend(); ax2.grid(True)

# Data buffers
t_buf, z_buf, z_ref_buf = [], [], []
roll_buf, pitch_buf, yaw_buf = [], [], []


# ----------------------------------------------------------
# 6️⃣ Main control loop
# ----------------------------------------------------------
print("🚀 Running drone controller with altitude + attitude control...")

while robot.step(dt) != -1:
    # 6.1 Read sensors
    t = robot.getTime()
    roll, pitch, yaw = imu.getRollPitchYaw()  # orientation [rad]
    p, q, r = gyro.getValues()                # angular rates [rad/s]
    z = gps.getValues()[2]                    # altitude [m]

    # 6.2 Altitude PD control
    z_error = target_alt - z
    dz_error = (z_error - z_error_prev) / (dt / 1000.0)
    z_error_prev = z_error
    u_z = Kp_z * z_error + Kd_z * dz_error
    thrust = clamp(T0 + u_z, 0, 100)

    # 6.3 Attitude PD control (roll, pitch) + yaw damping
    u_phi   = Kp_phi * clamp(roll,  -1.0, 1.0) + Kd_phi * p
    u_theta = Kp_the * clamp(pitch, -1.0, 1.0) + Kd_the * q
    u_psi   = Kd_psi * r  # only damping, no yaw command

    # 6.4 Mixer: combine altitude + attitude corrections
    FL = thrust - u_phi + u_theta - u_psi
    FR = thrust + u_phi + u_theta + u_psi
    RL = thrust - u_phi - u_theta + u_psi
    RR = thrust + u_phi - u_theta - u_psi

    # 6.5 Apply to motors
    # Signs may differ depending on propeller orientation in Webots.
    mFL.setVelocity( FL)
    mFR.setVelocity(-FR)
    mRL.setVelocity(-RL)
    mRR.setVelocity( RR)

    # 6.6 Update data buffers for plotting
    t_buf.append(t)
    z_buf.append(z)
    z_ref_buf.append(target_alt)
    roll_buf.append(math.degrees(roll))
    pitch_buf.append(math.degrees(pitch))
    yaw_buf.append(math.degrees(yaw))

    # 6.7 Refresh live plots
    # --- Altitude ---
    line_z.set_data(t_buf, z_buf)
    line_z_ref.set_data(t_buf, z_ref_buf)
    ax1.relim(); ax1.autoscale_view()

    # --- Attitude ---
    line_roll.set_data(t_buf, roll_buf)
    line_pitch.set_data(t_buf, pitch_buf)
    line_yaw.set_data(t_buf, yaw_buf)
    ax2.relim(); ax2.autoscale_view()

    plt.pause(0.001)

print("✅ Simulation ended.")