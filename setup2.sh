# Set the time
hwclock -w
# Calibrate IMU
minimu9-ahrs-calibrate --i2c-bus=/dev/i2c-1
