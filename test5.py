import sys
import os
import math
import asyncio
import threading
import simpleaudio as sa
from bleak import BleakScanner
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Localization Setup
languages = {
    "en": {
        "window_title": "Radar Interface",
        "error_beep": "Error: beep.wav not found at {}",
        "device_label": "{} ({} dBm)"
    },
    "es": {
        "window_title": "Interfaz de Radar",
        "error_beep": "Error: beep.wav no encontrado en {}",
        "device_label": "{} ({} dBm)"
    },
    "fr": {
        "window_title": "Interface Radar",
        "error_beep": "Erreur : beep.wav non trouvé à {}",
        "device_label": "{} ({} dBm)"
    }
}

current_language = "en"

def _(text_key, *args):
    return languages[current_language].get(text_key, text_key).format(*args)

# Window dimensions
width, height = 800, 600
center_x, center_y = 0, 0
radius = 200

# Radar state variables
sweep_angle = 0.0
paused = False
color_mode = 0  # 0: Green theme, 1: Blue theme, 2: Orange theme
blink_state = True  # State for blinking effect
sweep_speed = 2.0  # Degrees per update

# Button coordinates
button_size = 50
play_button_pos = (-width // 2 + 60, height // 2 - 60)
close_button_pos = (width // 2 - 60, height // 2 - 60)

# Bluetooth devices
devices = []
known_devices = {}
data_lock = threading.Lock()

# Determine script directory and set beep file path
script_dir = os.path.dirname(os.path.abspath(__file__))
beep_path = os.path.join(script_dir, "beep.wav")

# Verify that the beep file exists
if not os.path.isfile(beep_path):
    print(_("error_beep", beep_path))
    sys.exit(1)

# Load sound
sound_wave = sa.WaveObject.from_wave_file(beep_path)

async def scan_devices():
    global devices, known_devices
    scanner = BleakScanner()
    found_devices = await scanner.discover()

    new_devices = []
    with data_lock:
        lost_devices = set(known_devices.keys())

        for device in found_devices:
            name = device.name or "Unknown Device"
            rssi = device.rssi
            address = device.address
            if address not in known_devices:
                print(f"New device detected: {name} ({address})")
            known_devices[address] = (name, rssi)
            new_devices.append((name, rssi, address))
            if address in lost_devices:
                lost_devices.remove(address)

        # Remove lost devices
        for lost in lost_devices:
            lost_name, lost_rssi = known_devices[lost]
            print(f"DEVICE LOST: {lost_name} ({lost})")
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
    gluPerspective(45, (w / h) if h != 0 else 1, 0.1, 1000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def midpoint_circle(x0, y0, r):
    x = 0
    y = r
    d = 1 - r
    glBegin(GL_POINTS)
    while x <= y:
        glVertex3i(x0 + x, y0 + y, 0)
        glVertex3i(x0 - x, y0 + y, 0)
        glVertex3i(x0 + x, y0 - y, 0)
        glVertex3i(x0 - x, y0 - y, 0)
        glVertex3i(x0 + y, y0 + x, 0)
        glVertex3i(x0 - y, y0 + x, 0)
        glVertex3i(x0 + y, y0 - x, 0)
        glVertex3i(x0 - y, y0 - x, 0)
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1
    glEnd()

def midpoint_line(x0, y0, z0, x1, y1, z1):
    dx = x1 - x0
    dy = y1 - y0
    dz = z1 - z0
    steps = max(abs(dx), abs(dy), abs(dz))
    if steps == 0:
        glVertex3i(x0, y0, z0)
        return
    Xinc = dx / float(steps)
    Yinc = dy / float(steps)
    Zinc = dz / float(steps)
    x = x0
    y = y0
    z = z0
    glBegin(GL_LINES)
    glVertex3f(x, y, z)
    for _ in range(int(steps)):
        x += Xinc
        y += Yinc
        z += Zinc
        glVertex3f(x, y, z)
    glEnd()

def get_colors():
    if color_mode == 0:
        # Classic Green Radar
        return {
            "background": (0.0, 0.0, 0.0),
            "radar_line": (0.0, 1.0, 0.0),
            "sweep_line": (0.0, 1.0, 0.0),
            "button_fill": (0.0, 0.6, 0.0),
            "button_outline": (1.0, 1.0, 1.0),
            "button_symbol": (1.0, 1.0, 1.0),
            "device_color_on": (1.0, 0.0, 0.0),
            "device_color_off": (0.5, 0.0, 0.0),
            "heatmap_colors": [(0.0, 0.0, 1.0), (0.0, 1.0, 0.0), (1.0, 1.0, 0.0)],
            "text_color": (1.0, 1.0, 1.0)
        }
    elif color_mode == 1:
        # Blue Theme
        return {
            "background": (0.0, 0.0, 0.1),
            "radar_line": (0.0, 1.0, 1.0),
            "sweep_line": (0.0, 1.0, 1.0),
            "button_fill": (0.0, 0.3, 0.6),
            "button_outline": (1.0, 1.0, 1.0),
            "button_symbol": (1.0, 1.0, 1.0),
            "device_color_on": (1.0, 1.0, 0.0),
            "device_color_off": (0.5, 0.5, 0.0),
            "heatmap_colors": [(0.0, 0.0, 1.0), (0.0, 1.0, 1.0), (1.0, 1.0, 1.0)],
            "text_color": (1.0, 1.0, 1.0)
        }
    else:
        # Orange Theme
        return {
            "background": (0.1, 0.05, 0.0),
            "radar_line": (1.0, 0.5, 0.0),
            "sweep_line": (1.0, 0.7, 0.0),
            "button_fill": (0.6, 0.3, 0.0),
            "button_outline": (1.0, 1.0, 1.0),
            "button_symbol": (1.0, 1.0, 1.0),
            "device_color_on": (0.0, 1.0, 0.0),
            "device_color_off": (0.0, 0.5, 0.0),
            "heatmap_colors": [(1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (1.0, 1.0, 1.0)],
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
        midpoint_line(center_x, center_y, 0, x_end, y_end, 0)

def draw_sweep_line(angle):
    c = get_colors()
    if paused:
        glColor3f(c["sweep_line"][0] * 0.5, c["sweep_line"][1] * 0.5, c["sweep_line"][2] * 0.5)
    else:
        glColor3f(*c["sweep_line"])
    x_end = int(radius * math.cos(angle))
    y_end = int(radius * math.sin(angle))
    midpoint_line(center_x, center_y, 0, x_end, y_end, 0)

def draw_heatmap():
    c = get_colors()
    with data_lock:
        current_devices = list(devices)
    heatmap = {}
    for idx, (name, rssi, address) in enumerate(current_devices):
        # Simple grid-based heatmap
        angle = math.radians(45 * idx)
        distance = max(radius - ((rssi + 100) * 2), 0)
        x = int(distance * math.cos(angle))
        y = int(distance * math.sin(angle))
        key = (x // 50, y // 50)
        heatmap[key] = heatmap.get(key, 0) + 1

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    for (gx, gy), count in heatmap.items():
        intensity = min(count / 5.0, 1.0)
        if intensity > 0:
            color = c["heatmap_colors"][min(int(intensity * len(c["heatmap_colors"])), len(c["heatmap_colors"]) - 1)]
            glColor4f(color[0], color[1], color[2], intensity * 0.5)
            glBegin(GL_QUADS)
            glVertex3f(gx * 50, gy * 50, -1)
            glVertex3f((gx + 1) * 50, gy * 50, -1)
            glVertex3f((gx + 1) * 50, (gy + 1) * 50, -1)
            glVertex3f(gx * 50, (gy + 1) * 50, -1)
            glEnd()
    glDisable(GL_BLEND)

def draw_devices():
    global devices, blink_state
    c = get_colors()
    
    # Acquire lock before accessing devices
    with data_lock:
        current_devices = list(devices)
    
    # Save current OpenGL state
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    
    glPointSize(8)
    glBegin(GL_POINTS)
    for idx, (name, rssi, address) in enumerate(current_devices[:20]):  # Limiting to 20 devices
        # Map RSSI to distance (closer (stronger signal) means closer to center)
        distance = max(radius - ((rssi + 100) * 2), 0)
        
        # Spread devices around radar
        angle = math.radians(45 * idx)
        x = int(distance * math.cos(angle))
        y = int(distance * math.sin(angle))

        # Set color based on blink state
        if blink_state:
            glColor3f(*c["device_color_on"])
        else:
            glColor3f(*c["device_color_off"])
        
        glVertex3i(x, y, 0)
    glEnd()

    # Draw device labels
    glColor3f(*c["text_color"])
    for idx, (name, rssi, address) in enumerate(current_devices[:20]):
        distance = max(radius - ((rssi + 100) * 2), 0)
        angle = math.radians(45 * idx)
        x = int(distance * math.cos(angle))
        y = int(distance * math.sin(angle))
        glRasterPos3f(x + 10, y + 10, 0)
        text = _("device_label", name[:8], rssi)
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(ch))
    
    # Restore OpenGL state
    glPopAttrib()

def draw_buttons_2d():
    c = get_colors()

    # Switch to orthographic projection for 2D buttons
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(-width / 2, width / 2, -height / 2, height / 2)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Disable depth testing for UI elements
    glDisable(GL_DEPTH_TEST)

    # Play/Pause Button
    px, py = play_button_pos
    button_size_half = button_size // 2
    glColor3f(*c["button_fill"])
    glBegin(GL_QUADS)
    glVertex2f(px - button_size_half, py - button_size_half)
    glVertex2f(px + button_size_half, py - button_size_half)
    glVertex2f(px + button_size_half, py + button_size_half)
    glVertex2f(px - button_size_half, py + button_size_half)
    glEnd()

    # Button outline
    glColor3f(*c["button_outline"])
    glLineWidth(2)
    glBegin(GL_LINE_LOOP)
    glVertex2f(px - button_size_half, py - button_size_half)
    glVertex2f(px + button_size_half, py - button_size_half)
    glVertex2f(px + button_size_half, py + button_size_half)
    glVertex2f(px - button_size_half, py + button_size_half)
    glEnd()

    # Play/Pause Symbol
    glColor3f(*c["button_symbol"])
    if paused:
        # Pause symbol: two vertical bars
        bar_width = 8
        bar_height = 20
        glBegin(GL_QUADS)
        glVertex2f(px - 12, py - bar_height / 2)
        glVertex2f(px - 12 + bar_width, py - bar_height / 2)
        glVertex2f(px - 12 + bar_width, py + bar_height / 2)
        glVertex2f(px - 12, py + bar_height / 2)
        
        glVertex2f(px + 4, py - bar_height / 2)
        glVertex2f(px + 4 + bar_width, py - bar_height / 2)
        glVertex2f(px + 4 + bar_width, py + bar_height / 2)
        glVertex2f(px + 4, py + bar_height / 2)
        glEnd()
    else:
        # Play symbol: right-pointing triangle
        glBegin(GL_TRIANGLES)
        glVertex2f(px - 10, py - 15)
        glVertex2f(px - 10, py + 15)
        glVertex2f(px + 15, py)
        glEnd()

    # Close Button
    cx, cy = close_button_pos
    glColor3f(*c["button_fill"])
    glBegin(GL_QUADS)
    glVertex2f(cx - button_size_half, cy - button_size_half)
    glVertex2f(cx + button_size_half, cy - button_size_half)
    glVertex2f(cx + button_size_half, cy + button_size_half)
    glVertex2f(cx - button_size_half, cy + button_size_half)
    glEnd()

    # Button outline
    glColor3f(*c["button_outline"])
    glLineWidth(2)
    glBegin(GL_LINE_LOOP)
    glVertex2f(cx - button_size_half, cy - button_size_half)
    glVertex2f(cx + button_size_half, cy - button_size_half)
    glVertex2f(cx + button_size_half, cy + button_size_half)
    glVertex2f(cx - button_size_half, cy + button_size_half)
    glEnd()

    # Close Symbol (X)
    glColor3f(*c["button_symbol"])
    glLineWidth(2)
    glBegin(GL_LINES)
    glVertex2f(cx - 15, cy - 15)
    glVertex2f(cx + 15, cy + 15)
    glVertex2f(cx - 15, cy + 15)
    glVertex2f(cx + 15, cy - 15)
    glEnd()

    # Restore projection and modelview matrices
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def fill_rectangle(x_min, x_max, y_min, y_max, z, color):
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex3f(x_min, y_min, z)
    glVertex3f(x_max, y_min, z)
    glVertex3f(x_max, y_max, z)
    glVertex3f(x_min, y_max, z)
    glEnd()

def draw_buttons_2d_overlay():
    draw_buttons_2d()

def draw_heatmap_overlay():
    draw_heatmap()

def draw_buttons():
    # No longer used since buttons are drawn in 2D overlay
    pass

def display():
    c = get_colors()
    glClearColor(*c["background"], 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Set camera
    gluLookAt(0, -400, 300, 0, 0, 0, 0, 0, 1)

    # Enable depth testing
    glEnable(GL_DEPTH_TEST)

    draw_radar()
    draw_sweep_line(math.radians(sweep_angle))
    draw_devices()
    draw_heatmap_overlay()

    # Draw 2D buttons on top
    draw_buttons_2d_overlay()

    glutSwapBuffers()

def update(value):
    global sweep_angle, blink_state
    previous_angle = sweep_angle

    blink_state = not blink_state

    if not paused:
        sweep_angle += sweep_speed
        if sweep_angle >= 360.0:
            sweep_angle -= 360.0

    if previous_angle > sweep_angle and not paused:
        sound_wave.play()

    glutPostRedisplay()
    glutTimerFunc(int(1000 / 60), update, 0)  # 60 FPS for smoother animation

def on_mouse_click(button, state, mx, my):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Convert window coordinates to orthographic 2D coordinates
        world_x = mx - width / 2
        world_y = height / 2 - my

        # Play/Pause button boundaries
        px, py = play_button_pos
        half_size = 25  # button_size_half
        if (px - half_size <= world_x <= px + half_size) and (py - half_size <= world_y <= py + half_size):
            toggle_play_pause()
            return

        # Close button boundaries
        cx, cy = close_button_pos
        if (cx - half_size <= world_x <= cx + half_size) and (cy - half_size <= world_y <= cy + half_size):
            print("PROJECT TERMINATED")
            close_application()
            return

def on_keyboard(key, x, y):
    global color_mode, sweep_speed
    if key in [b'm', b'M']:
        color_mode = (color_mode + 1) % 3
        glutPostRedisplay()
    elif key == b'\x1b':  # ESC key
        close_application()

def on_special(key, x, y):
    global sweep_speed
    if key == GLUT_KEY_RIGHT:
        sweep_speed += 1.0
        print(f"Sweep speed increased to {sweep_speed} degrees per update.")
    elif key == GLUT_KEY_LEFT:
        sweep_speed = max(1.0, sweep_speed - 1.0)
        print(f"Sweep speed decreased to {sweep_speed} degrees per update.")

def toggle_play_pause():
    global paused
    paused = not paused
    state = "Paused" if paused else "Playing"
    print(f"Radar {state}.")

def close_application():
    glutLeaveMainLoop()
    sys.exit(0)

def main():
    # Initial scan before starting
    scan_thread = threading.Thread(target=asyncio.run, args=(scan_devices(),))
    scan_thread.start()

    # Play the sound at startup
    sound_wave.play()

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutCreateWindow(bytes(_("window_title"), 'utf-8'))
    reshape(width, height)
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(on_mouse_click)
    glutKeyboardFunc(on_keyboard)
    glutSpecialFunc(on_special)
    glutTimerFunc(int(1000 / 60), update, 0)  # Start at 60 FPS
    glutMainLoop()

if __name__ == '__main__':
    main()
