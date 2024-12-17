import sys
import os
import math
import asyncio
import simpleaudio as sa
from bleak import BleakScanner
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Window dimensions
width, height = 600, 600
center_x, center_y = 0, 0
radius = 200

# Radar state variables
sweep_angle = 0.0
paused = False
color_mode = 0  # 0: Green theme, 1: Blue theme, 2: Orange theme
blink_state = True  # State for blinking effect

# Button coordinates
button_y_top = 280
button_y_bottom = 250
reset_button_x_min = -250
reset_button_x_max = -200
play_button_x_min = -25
play_button_x_max = 25
close_button_x_min = 200
close_button_x_max = 250

# Bluetooth devices
devices = []
known_devices = {}

# Determine script directory and set beep file path
script_dir = os.path.dirname(os.path.abspath(__file__))
beep_path = os.path.join(script_dir, "beep.wav")

# Load sound
sound_wave = sa.WaveObject.from_wave_file(beep_path)

async def scan_devices():
    global devices, known_devices
    scanner = BleakScanner()
    found_devices = await scanner.discover()

    new_devices = []
    lost_devices = set(known_devices.keys())

    for device in found_devices:
        name = device.name or "Unknown Device"
        rssi = device.rssi
        address = device.address
        known_devices[address] = (name, rssi)
        new_devices.append((name, rssi, address))
        if address in lost_devices:
            lost_devices.remove(address)

    # Remove lost devices
    for lost in lost_devices:
        print(f"UPDATE: {known_devices[lost][0]} ({lost}) device lost")
        del known_devices[lost]

    # Update device list
    devices = sorted(new_devices, key=lambda x: x[1], reverse=True)
    print(f"Total Devices: {len(devices)}")
    for name, rssi, address in devices:
        print(f"Device: {name}, RSSI: {rssi}, Address: {address}")

def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-width/2, width/2, -height/2, height/2, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def midpoint_circle(x0, y0, r):
    x = 0
    y = r
    d = 1 - r
    glBegin(GL_POINTS)
    while x <= y:
        glVertex2i(x0 + x, y0 + y)
        glVertex2i(x0 - x, y0 + y)
        glVertex2i(x0 + x, y0 - y)
        glVertex2i(x0 - x, y0 - y)
        glVertex2i(x0 + y, y0 + x)
        glVertex2i(x0 - y, y0 + x)
        glVertex2i(x0 + y, y0 - x)
        glVertex2i(x0 - y, y0 - x)
        if d < 0:
            d += 2*x + 3
        else:
            d += 2*(x - y) + 5
            y -= 1
        x += 1
    glEnd()

def midpoint_line(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0
    steep = abs(dy) > abs(dx)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0
    dx = x1 - x0
    dy = y1 - y0
    yi = 1 if dy >= 0 else -1
    dy = abs(dy)
    D = 2*dy - dx
    y = y0
    glBegin(GL_POINTS)
    for x in range(x0, x1+1):
        if steep:
            glVertex2i(y, x)
        else:
            glVertex2i(x, y)
        if D > 0:
            y += yi
            D -= 2*dx
        D += 2*dy
    glEnd()

def get_colors():
    if color_mode == 0:
        # Classic Green Radar
        return {
            "background": (0.0, 0.0, 0.0),
            "radar_line": (0.0, 1.0, 0.0),
            "sweep_line": (0.0, 1.0, 0.0),
            "button_fill": (0.2, 0.2, 0.2),
            "button_outline": (1.0, 1.0, 1.0),
            "button_symbol": (0.0, 1.0, 0.0),
            "device_color_on": (1.0, 0.0, 0.0),
            "device_color_off": (0.5, 0.0, 0.0),
            "text_color": (1.0, 1.0, 1.0)
        }
    elif color_mode == 1:
        # Blue Theme
        return {
            "background": (0.0, 0.0, 0.1),
            "radar_line": (0.0, 1.0, 1.0),
            "sweep_line": (0.0, 1.0, 1.0),
            "button_fill": (0.0, 0.0, 0.2),
            "button_outline": (1.0, 1.0, 1.0),
            "button_symbol": (1.0, 1.0, 1.0),
            "device_color_on": (1.0, 1.0, 0.0),
            "device_color_off": (0.5, 0.5, 0.0),
            "text_color": (1.0, 1.0, 1.0)
        }
    else:
        # Orange Theme
        return {
            "background": (0.1, 0.05, 0.0),
            "radar_line": (1.0, 0.5, 0.0),
            "sweep_line": (1.0, 0.7, 0.0),
            "button_fill": (0.2, 0.2, 0.2),
            "button_outline": (1.0, 1.0, 1.0),
            "button_symbol": (1.0, 0.5, 0.0),
            "device_color_on": (0.0, 1.0, 0.0),
            "device_color_off": (0.0, 0.5, 0.0),
            "text_color": (1.0, 1.0, 1.0)
        }

def draw_radar():
    c = get_colors()
    glColor3f(*c["radar_line"])

    # Outer circle + inner circles
    midpoint_circle(center_x, center_y, radius)
    num_circles = 4
    step = radius // num_circles
    for i in range(1, num_circles):
        r = step * i
        midpoint_circle(center_x, center_y, r)

    # Radial lines at every 45 degrees
    for angle_deg in range(0, 360, 45):
        angle_rad = math.radians(angle_deg)
        x_end = int(radius * math.cos(angle_rad))
        y_end = int(radius * math.sin(angle_rad))
        midpoint_line(center_x, center_y, x_end, y_end)

def draw_sweep_line(angle):
    c = get_colors()
    if paused:
        glColor3f(c["sweep_line"][0]*0.5, c["sweep_line"][1]*0.5, c["sweep_line"][2]*0.5)
    else:
        glColor3f(*c["sweep_line"])
    x_end = int(radius * math.cos(angle))
    y_end = int(radius * math.sin(angle))
    midpoint_line(center_x, center_y, x_end, y_end)

def draw_devices():
    global devices, blink_state
    c = get_colors()
    for idx, (name, rssi, address) in enumerate(devices):
        # Map RSSI to distance (closer (stronger signal) means closer to center)
        # RSSI typically ranges around -30 (very close) to -100 (far)
        # We'll just map: distance = radius - ((rssi + 100)*2)
        distance = radius - ((rssi + 100) * 2)
        if distance < 0:
            distance = 0
        # Spread devices around radar
        angle = math.radians(45 * idx)
        x = int(distance * math.cos(angle))
        y = int(distance * math.sin(angle))

        glPointSize(8)
        glBegin(GL_POINTS)
        if blink_state:
            glColor3f(*c["device_color_on"])
        else:
            glColor3f(*c["device_color_off"])
        glVertex2i(x, y)
        glEnd()

        # Draw text (device info)
        glColor3f(*c["text_color"])
        glRasterPos2i(x + 10, y + 10)
        text = f"{name[:8]} ({rssi} dBm)"
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))

def fill_rectangle(x_min, x_max, y_min, y_max, color):
    glColor3f(*color)
    glBegin(GL_POINTS)
    for x in range(x_min, x_max+1):
        for y in range(y_min, y_max+1):
            glVertex2i(x, y)
    glEnd()

def draw_button_outline(x_min, x_max, y_min, y_max, color):
    glColor3f(*color)
    midpoint_line(x_min, y_max, x_max, y_max)
    midpoint_line(x_min, y_min, x_max, y_min)
    midpoint_line(x_min, y_min, x_min, y_max)
    midpoint_line(x_max, y_min, x_max, y_max)

def draw_reset_symbol(x_center, y_center, color):
    glColor3f(*color)
    # "R" like shape
    midpoint_line(x_center-3, y_center-3, x_center-3, y_center+3)
    midpoint_line(x_center-3, y_center+3, x_center+1, y_center+3)
    midpoint_line(x_center-3, y_center, x_center+1, y_center)
    midpoint_line(x_center-1, y_center, x_center+2, y_center-3)

def draw_play_pause_symbol(x_center, y_center, symbol_color):
    glColor3f(*symbol_color)
    if paused:
        # Play symbol: right triangle
        midpoint_line(x_center-3, y_center-3, x_center+4, y_center)
        midpoint_line(x_center+4, y_center, x_center-3, y_center+3)
        midpoint_line(x_center-3, y_center-3, x_center-3, y_center+3)
    else:
        # Pause symbol
        midpoint_line(x_center-2, y_center-3, x_center-2, y_center+3)
        midpoint_line(x_center+2, y_center-3, x_center+2, y_center+3)

def draw_close_symbol(x_center, y_center, color):
    glColor3f(*color)
    midpoint_line(x_center-3, y_center-3, x_center+3, y_center+3)
    midpoint_line(x_center-3, y_center+3, x_center+3, y_center-3)

def draw_buttons():
    c = get_colors()
    # Reset Button
    fill_rectangle(reset_button_x_min, reset_button_x_max, button_y_bottom, button_y_top, c["button_fill"])
    draw_button_outline(reset_button_x_min, reset_button_x_max, button_y_bottom, button_y_top, c["button_outline"])
    draw_reset_symbol((reset_button_x_min+reset_button_x_max)//2, (button_y_bottom+button_y_top)//2, c["button_symbol"])

    # Play/Pause Button
    fill_rectangle(play_button_x_min, play_button_x_max, button_y_bottom, button_y_top, c["button_fill"])
    draw_button_outline(play_button_x_min, play_button_x_max, button_y_bottom, button_y_top, c["button_outline"])
    draw_play_pause_symbol((play_button_x_min+play_button_x_max)//2, (button_y_bottom+button_y_top)//2, c["button_symbol"])

    # Close Button
    fill_rectangle(close_button_x_min, close_button_x_max, button_y_bottom, button_y_top, c["button_fill"])
    draw_button_outline(close_button_x_min, close_button_x_max, button_y_bottom, button_y_top, c["button_outline"])
    draw_close_symbol((close_button_x_min+close_button_x_max)//2, (button_y_bottom+button_y_top)//2, c["button_symbol"])

def display():
    c = get_colors()
    glClearColor(*c["background"], 1.0)
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    draw_radar()
    draw_sweep_line(math.radians(sweep_angle))
    draw_devices()
    draw_buttons()

    glutSwapBuffers()

def update(value):
    global sweep_angle, blink_state
    previous_angle = sweep_angle

    # Toggle blink state less frequently
    # For simplicity, toggle every update call
    blink_state = not blink_state

    if not paused:
        sweep_angle += 2.0
        if sweep_angle >= 360.0:
            sweep_angle -= 360.0

    # If we completed a rotation (meaning sweep_angle passed through 0 again),
    # then play the beep.
    if previous_angle > sweep_angle and not paused:
        sound_wave.play()

    glutPostRedisplay()
    glutTimerFunc(500, update, 0)

def on_mouse_click(button, state, mx, my):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        world_x = mx - width/2
        world_y = (height/2) - my

        # Reset button
        if (reset_button_x_min <= world_x <= reset_button_x_max and
            button_y_bottom <= world_y <= button_y_top):
            reset_action()

        # Play/Pause button
        elif (play_button_x_min <= world_x <= play_button_x_max and
              button_y_bottom <= world_y <= button_y_top):
            toggle_play_pause()

        # Close button
        elif (close_button_x_min <= world_x <= close_button_x_max and
              button_y_bottom <= world_y <= button_y_top):
            close_application()

def on_keyboard(key, x, y):
    global color_mode
    if key == b'm' or key == b'M':
        color_mode = (color_mode + 1) % 3
        glutPostRedisplay()

def reset_action():
    global sweep_angle, devices, known_devices
    sweep_angle = 0.0
    devices = []
    known_devices = {}
    print("radar reset")
    # Re-scan devices
    asyncio.run(scan_devices())
    # Devices updated and displayed again

def toggle_play_pause():
    global paused
    paused = not paused

def close_application():
    glutLeaveMainLoop()
    sys.exit(0)

def main():
    # Initial scan before starting
    asyncio.run(scan_devices())

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(width, height)
    glutCreateWindow(b"Radar Interface")
    reshape(width, height)
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(on_mouse_click)
    glutKeyboardFunc(on_keyboard)
    # Start update timer with 500ms interval for blinking and rotation
    glutTimerFunc(500, update, 0)
    glutMainLoop()

if __name__ == '__main__':
    main()