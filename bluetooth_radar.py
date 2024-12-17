# bluetooth_radar.py

import sys
import time
import math
import threading
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import bluetooth

# Radar parameters
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800
RADAR_RADIUS = 300
SWEEP_SPEED = 90  # degrees per second
SWEEP_COLOR = (0.0, 1.0, 0.0)  # Green
RADAR_COLOR = (0.0, 1.0, 0.0)  # Green
BLIP_COLOR = (1.0, 0.0, 0.0)   # Red
BLIP_SIZE = 5  # Size multiplier for blips

# Shared data structure for Bluetooth devices
bluetooth_devices = []
bluetooth_lock = threading.Lock()

# Sweep angle
sweep_angle = 0.0

def midpoint_circle(cx, cy, r):
    """Generate points for a circle using the Midpoint Circle Algorithm."""
    points = []
    x = r
    y = 0
    decision_over2 = 1 - x  # Decision parameter

    while y <= x:
        points.extend([
            (cx + x, cy + y),
            (cx + y, cy + x),
            (cx - y, cy + x),
            (cx - x, cy + y),
            (cx - x, cy - y),
            (cx - y, cy - x),
            (cx + y, cy - x),
            (cx + x, cy - y),
        ])
        y += 1
        if decision_over2 <= 0:
            decision_over2 += 2 * y + 1
        else:
            x -= 1
            decision_over2 += 2 * (y - x) + 1
    return points

def midpoint_line(x0, y0, x1, y1):
    """Generate points for a line using the Midpoint Line Algorithm."""
    points = []

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0

    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1

    if dy <= dx:
        err = dx / 2.0
        while x != x1:
            points.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            points.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    points.append((x, y))
    return points

def scan_bluetooth_devices():
    """Thread function to continuously scan for Bluetooth devices."""
    global bluetooth_devices
    while True:
        try:
            devices = bluetooth.discover_devices(lookup_names=True)
            with bluetooth_lock:
                bluetooth_devices = devices
        except Exception as e:
            print(f"Error scanning Bluetooth devices: {e}")
        time.sleep(5)  # Scan every 5 seconds

def get_rotated_point(cx, cy, angle_deg, radius):
    """Calculate a point rotated by angle_deg around (cx, cy) at a given radius."""
    angle_rad = math.radians(angle_deg)
    x = cx + radius * math.cos(angle_rad)
    y = cy + radius * math.sin(angle_rad)
    return (x, y)

def draw_circle(cx, cy, r):
    """Draw a circle using GL_POINTS and the Midpoint Circle Algorithm."""
    points = midpoint_circle(cx, cy, r)
    glColor3f(*RADAR_COLOR)
    glBegin(GL_POINTS)
    for point in points:
        glVertex2f(point[0], point[1])
    glEnd()

def draw_line(cx, cy, angle_deg):
    """Draw the sweep line using GL_POINTS and the Midpoint Line Algorithm."""
    end_x, end_y = get_rotated_point(cx, cy, angle_deg, RADAR_RADIUS)
    points = midpoint_line(int(cx), int(cy), int(end_x), int(end_y))
    glColor3f(*SWEEP_COLOR)
    glBegin(GL_POINTS)
    for point in points:
        glVertex2f(point[0], point[1])
    glEnd()

def draw_blips(cx, cy):
    """Draw blips for each detected Bluetooth device."""
    with bluetooth_lock:
        devices = list(bluetooth_devices)

    glColor3f(*BLIP_COLOR)
    glBegin(GL_POINTS)
    for device in devices:
        # Map device to a position on the radar
        # For simplicity, assign random angles and distances within the radar
        # In a real scenario, you might use signal strength or other metrics
        angle = (hash(device[0]) % 360)  # Unique angle based on device address
        distance = (hash(device[0]) % RADAR_RADIUS)
        x = cx + distance * math.cos(math.radians(angle))
        y = cy + distance * math.sin(math.radians(angle))
        # Draw a larger point for the blip
        for dx in range(-BLIP_SIZE, BLIP_SIZE + 1):
            for dy in range(-BLIP_SIZE, BLIP_SIZE + 1):
                if dx*dx + dy*dy <= BLIP_SIZE*BLIP_SIZE:
                    glVertex2f(x + dx, y + dy)
    glEnd()

def display():
    """OpenGL display callback."""
    global sweep_angle
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Draw radar circle
    draw_circle(0, 0, RADAR_RADIUS)

    # Draw sweep line
    draw_line(0, 0, sweep_angle)

    # Draw blips
    draw_blips(0, 0)

    glutSwapBuffers()

def idle():
    """Idle callback to update sweep angle and request redraw."""
    global sweep_angle
    # Update sweep angle based on sweep speed and frame time
    sweep_angle += SWEEP_SPEED * (1/60.0)  # Assuming ~60 FPS
    sweep_angle = sweep_angle % 360
    glutPostRedisplay()

def init_opengl():
    """Initialize OpenGL settings."""
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Black background
    glPointSize(2.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-WINDOW_WIDTH/2, WINDOW_WIDTH/2, -WINDOW_HEIGHT/2, WINDOW_HEIGHT/2)
    glMatrixMode(GL_MODELVIEW)

def main():
    """Main function to set up OpenGL and start threads."""
    # Start Bluetooth scanning thread
    bt_thread = threading.Thread(target=scan_bluetooth_devices, daemon=True)
    bt_thread.start()

    # Initialize OpenGL and GLUT
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Bluetooth Radar Simulation")
    init_opengl()

    # Register callbacks
    glutDisplayFunc(display)
    glutIdleFunc(idle)

    # Enter the GLUT main loop
    glutMainLoop()

if __name__ == "__main__":
    main()
