from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

width, height = 600, 600
center_x, center_y = 0, 0
radius = 200
sweep_angle = 0.0

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

def draw_radar():
    glColor3f(0.0, 1.0, 0.0)
    midpoint_circle(center_x, center_y, radius)

    num_circles = 4
    step = radius // num_circles
    for i in range(1, num_circles):
        r = step * i
        midpoint_circle(center_x, center_y, r)

    for angle_deg in range(0, 360, 45):
        angle_rad = math.radians(angle_deg)
        x_end = int(radius * math.cos(angle_rad))
        y_end = int(radius * math.sin(angle_rad))
        midpoint_line(center_x, center_y, x_end, y_end)

def draw_sweep_line(angle):
    glColor3f(0.0, 1.0, 0.0)
    x_end = int(radius * math.cos(angle))
    y_end = int(radius * math.sin(angle))
    midpoint_line(center_x, center_y, x_end, y_end)

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    draw_radar()
    draw_sweep_line(math.radians(sweep_angle))
    draw_buttons()  # <-- Add this call to draw the buttons at the top

    glutSwapBuffers()

def update(value):
    global sweep_angle
    sweep_angle += 2.0
    if sweep_angle >= 360.0:
        sweep_angle -= 360.0
    glutPostRedisplay()
    glutTimerFunc(50, update, 0)

##################################
# New Code: Drawing the Buttons
##################################

def draw_rectangle_outline(x_min, y_min, x_max, y_max):
    # Draw rectangle outline using midpoint_line
    # Top edge
    midpoint_line(x_min, y_max, x_max, y_max)
    # Bottom edge
    midpoint_line(x_min, y_min, x_max, y_min)
    # Left edge
    midpoint_line(x_min, y_min, x_min, y_max)
    # Right edge
    midpoint_line(x_max, y_min, x_max, y_max)

def draw_letter_r(x_center, y_center):
    # A rough "R" made of lines:
    # Vertical line
    midpoint_line(x_center, y_center-5, x_center, y_center+5)
    # Top horizontal line
    midpoint_line(x_center, y_center+5, x_center+3, y_center+5)
    # Diagonal line for the leg
    midpoint_line(x_center, y_center, x_center+3, y_center-5)

def draw_play_pause(x_center, y_center):
    # Draw a ">" shape for play or "||" for pause.
    # Let's do a simple ">" by connecting points:
    midpoint_line(x_center-2, y_center-3, x_center+3, y_center)
    midpoint_line(x_center+3, y_center, x_center-2, y_center+3)

def draw_close_symbol(x_center, y_center):
    # Draw an "X" inside the box
    midpoint_line(x_center-3, y_center-3, x_center+3, y_center+3)
    midpoint_line(x_center-3, y_center+3, x_center+3, y_center-3)

def draw_buttons():
    glColor3f(1.0, 1.0, 1.0)  # White buttons for contrast

    # Coordinates for buttons (top of screen ~ y=280 to 300)
    button_y_top = 280
    button_y_bottom = 250

    # Left (Reset) button
    left_button_x_min = -250
    left_button_x_max = -200
    draw_rectangle_outline(left_button_x_min, button_y_bottom, left_button_x_max, button_y_top)
    draw_letter_r((left_button_x_min+left_button_x_max)//2, (button_y_bottom+button_y_top)//2)

    # Middle (Play/Pause) button
    mid_button_x_min = -25
    mid_button_x_max = 25
    draw_rectangle_outline(mid_button_x_min, button_y_bottom, mid_button_x_max, button_y_top)
    draw_play_pause((mid_button_x_min+mid_button_x_max)//2, (button_y_bottom+button_y_top)//2)

    # Right (Close) button
    right_button_x_min = 200
    right_button_x_max = 250
    draw_rectangle_outline(right_button_x_min, button_y_bottom, right_button_x_max, button_y_top)
    draw_close_symbol((right_button_x_min+right_button_x_max)//2, (button_y_bottom+button_y_top)//2)

##################################
# End of new code section
##################################

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(width, height)
    glutCreateWindow(b"Radar Interface with Buttons")
    glClearColor(0.0, 0.0, 0.0, 0.0)
    reshape(width, height)
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutTimerFunc(50, update, 0)
    glutMainLoop()

if __name__ == '__main__':
    main()
