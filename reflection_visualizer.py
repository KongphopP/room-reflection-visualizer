from matplotlib.widgets import Slider, TextBox, Button
import numpy as np
import matplotlib.pyplot as plt

# === INITIAL ROOM DIMENSIONS ===
W, D, H = 3.0, 5.0, 3.0

# === DEFAULT VALUES ===
default_source1_xy = [W / 4, 0.0]
default_z = 1.5
default_receiver_y = D * 0.7

# === STATE ===
source1_xy = default_source1_xy.copy()
source1_z = default_z
source2_z = default_z

# === UI STATE PLACEHOLDERS (textboxes) ===
textbox_w = textbox_d = textbox_h = None  # filled later

def get_sources():
    x1, y1 = source1_xy
    x2 = W - x1
    y2 = y1
    return [
        np.array([x1, y1, source1_z]),
        np.array([x2, y2, source2_z])
    ]

def get_receiver(y):
    return np.array([W / 2, y, 1.2])

def get_walls():
    return {
        "x0": lambda p: np.array([-p[0], p[1], p[2]]),
        "x1": lambda p: np.array([2 * W - p[0], p[1], p[2]]),
        "y0": lambda p: np.array([p[0], -p[1], p[2]]),
        "y1": lambda p: np.array([p[0], 2 * D - p[1], p[2]]),
        "z0": lambda p: np.array([p[0], p[1], -p[2]]),
        "z1": lambda p: np.array([p[0], p[1], 2 * H - p[2]])
    }

def intersection_point(img_src, rec, wall):
    src, rec = np.array(img_src), np.array(rec)
    dim = "xyz".index(wall[0])
    wall_pos = {"x": W, "y": D, "z": H}[wall[0]] if wall[1] == "1" else 0
    t = (wall_pos - src[dim]) / (rec[dim] - src[dim])
    if not (0 <= t <= 1): return None
    pt = src + t * (rec - src)
    for i in range(3):
        if i != dim and not (0 <= pt[i] <= [W, D, H][i]):
            return None
    return pt

def update_scene(receiver_y):
    global sources
    receiver = get_receiver(receiver_y)
    sources = get_sources()
    ax_top.clear()
    ax_side.clear()

    ax_top.set_title("Top View", pad=20)
    ax_top.set_xlim(0, W)
    ax_top.set_ylim(0, D)
    ax_top.set_aspect('equal')
    ax_top.grid(True)
    ax_top.set_xlabel("Width [m]")
    ax_top.set_ylabel("Depth [m]")

    ax_side.set_title("Side View", pad=20)
    ax_side.set_xlim(0, D)
    ax_side.set_ylim(0, H)
    ax_side.set_aspect('equal')
    ax_side.grid(True)
    ax_side.set_xlabel("Depth (Y) [m]")
    ax_side.set_ylabel("Height (Z) [m]")

    ax_top.plot([0, W, W, 0, 0], [0, 0, D, D, 0], color='gray')
    ax_side.plot([0, D, D, 0, 0], [0, 0, H, H, 0], color='gray')

    ax_top.plot(receiver[0], receiver[1], 'ro')
    ax_side.plot(receiver[1], receiver[2], 'ro')

    source_colors = ['blue', 'green']
    walls = get_walls()

    for idx, source in enumerate(sources):
        color = source_colors[idx]
        ax_top.plot(source[0], source[1], marker='v', color=color, markersize=10)
        ax_side.plot(source[1], source[2], marker='<', color=color, markersize=10)

        ax_top.plot([source[0], receiver[0]], [source[1], receiver[1]], '--', color='black')
        ax_side.plot([source[1], receiver[1]], [source[2], receiver[2]], '--', color='black')

        for wall, mirror_func in walls.items():
            img_src = mirror_func(source)
            refl = intersection_point(img_src, receiver, wall)
            if refl is not None:
                ax_top.plot([source[0], refl[0]], [source[1], refl[1]], '--', color=color)
                ax_side.plot([source[1], refl[1]], [source[2], refl[2]], '--', color=color)
                ax_top.plot([refl[0], receiver[0]], [refl[1], receiver[1]], '--', color='red')
                ax_side.plot([refl[1], receiver[1]], [refl[2], receiver[2]], '--', color='red')
                ax_top.plot(refl[0], refl[1], 'x', color='orange')
                ax_side.plot(refl[1], refl[2], 'x', color='orange')

                if wall.startswith("x"):
                    reflection_depth = round(refl[1], 2)
                    ax_top.text(refl[0] + 0.2, refl[1], f"{reflection_depth}", fontsize=10, color='black')
                if wall == "y1":
                    reflection_x = round(refl[0], 2)
                    ax_top.text(refl[0], refl[1] + 0.2, f"{reflection_x}", fontsize=10, color='black')
                if wall.startswith("z"):
                    reflection_y = round(refl[1], 2)
                    ax_side.text(refl[1] + 0.2, refl[2], f"{reflection_y}", fontsize=10, color='black')

    fig.canvas.draw_idle()

# === INTERACTION CALLBACKS ===
def on_slider_change(val):
    textbox_y.set_val(str(round(val, 2)))
    update_scene(val)

def on_text_submit_y(text):
    try:
        val = float(text)
        if 0.5 <= val <= D - 0.5:
            slider.set_val(val)
            update_scene(val)
    except ValueError:
        pass

def on_z_submit(text):
    global source1_z, source2_z
    try:
        val = float(text)
        if 0 <= val <= H:
            source1_z = val
            source2_z = val
            update_scene(slider.val)
    except ValueError:
        pass

def on_x_submit(text):
    try:
        val = float(text)
        if 0 <= val <= W:
            source1_xy[0] = val
            update_scene(slider.val)
    except ValueError:
        pass

def on_y_submit(text):
    try:
        val = float(text)
        if 0 <= val <= D:
            source1_xy[1] = val
            update_scene(slider.val)
    except ValueError:
        pass

def on_room_submit(_):
    global W, D, H, source1_xy
    try:
        new_W = float(textbox_w.text)
        new_D = float(textbox_d.text)
        new_H = float(textbox_h.text)
        if new_W > 0 and new_D > 0 and new_H > 0:
            W, D, H = new_W, new_D, new_H
            slider.valmax = D - 0.5
            slider.ax.set_xlim(slider.valmin, slider.valmax)
            source1_xy[0] = np.clip(source1_xy[0], 0, W)
            source1_xy[1] = np.clip(source1_xy[1], 0, D)
            slider.set_val(min(slider.val, D - 0.5))
            update_scene(slider.val)
    except:
        pass

def reset_sources(event):
    global source1_xy, source1_z, source2_z
    source1_xy = default_source1_xy.copy()
    source1_z = default_z
    source2_z = default_z
    slider.set_val(default_receiver_y)
    textbox_z.set_val(str(default_z))
    textbox_y.set_val(str(round(default_receiver_y, 2)))
    textbox_x.set_val(str(source1_xy[0]))
    textbox_xy.set_val(str(source1_xy[1]))
    textbox_w.set_val(str(W))
    textbox_d.set_val(str(D))
    textbox_h.set_val(str(H))
    update_scene(default_receiver_y)

# === MOUSE DRAG ===
dragging = False
def on_press(event):
    global dragging
    if event.inaxes == ax_top:
        x1, y1 = source1_xy
        if abs(event.xdata - x1) < 0.2 and abs(event.ydata - y1) < 0.2:
            dragging = True

def on_motion(event):
    if dragging and event.inaxes == ax_top:
        source1_xy[0] = np.clip(event.xdata, 0, W)
        source1_xy[1] = np.clip(event.ydata, 0, D)
        textbox_x.set_val(str(round(source1_xy[0], 2)))
        textbox_xy.set_val(str(round(source1_xy[1], 2)))
        update_scene(slider.val)

def on_release(event):
    global dragging
    dragging = False

# === PLOT SETUP ===
fig, (ax_top, ax_side) = plt.subplots(1, 2, figsize=(14, 6))
plt.subplots_adjust(left=0.1, bottom=0.45)
receiver_init = get_receiver(default_receiver_y)
sources = get_sources()
update_scene(default_receiver_y)

# === CONTROLS LAYOUT ===
# Row 1: Receiver Y (slider + input)
slider_ax = plt.axes([0.2, 0.36, 0.6, 0.04])
slider = Slider(slider_ax, "Receiver Y", 0.5, D - 0.5, valinit=default_receiver_y)
textbox_y_ax = plt.axes([0.8, 0.36, 0.05, 0.04])
textbox_y = TextBox(textbox_y_ax, "", initial=str(round(default_receiver_y, 2)))

# Row 2: Source X, Y, Z
x_ax = plt.axes([0.2, 0.28, 0.05, 0.04])
y_ax = plt.axes([0.35, 0.28, 0.05, 0.04])
z_ax = plt.axes([0.5, 0.28, 0.05, 0.04])
textbox_x = TextBox(x_ax, "Source X ", initial=str(default_source1_xy[0]))
textbox_xy = TextBox(y_ax, "Source Y ", initial=str(default_source1_xy[1]))
textbox_z = TextBox(z_ax, "Source Z ", initial=str(default_z))

# Row 3: Room size
textbox_w_ax = plt.axes([0.2, 0.18, 0.05, 0.04])
textbox_d_ax = plt.axes([0.35, 0.18, 0.05, 0.04])
textbox_h_ax = plt.axes([0.5, 0.18, 0.05, 0.04])
textbox_w = TextBox(textbox_w_ax, "Room Width ", initial=str(W))
textbox_d = TextBox(textbox_d_ax, "Room Depth ", initial=str(D))
textbox_h = TextBox(textbox_h_ax, "Room Height ", initial=str(H))

# Reset button
reset_ax = plt.axes([0.75, 0.2, 0.1, 0.05])
reset_button = Button(reset_ax, "Reset All")

# === EVENT BINDINGS ===
slider.on_changed(on_slider_change)
textbox_y.on_submit(on_text_submit_y)
textbox_z.on_submit(on_z_submit)
textbox_x.on_submit(on_x_submit)
textbox_xy.on_submit(on_y_submit)
textbox_w.on_submit(on_room_submit)
textbox_d.on_submit(on_room_submit)
textbox_h.on_submit(on_room_submit)
reset_button.on_clicked(reset_sources)
fig.canvas.mpl_connect("button_press_event", on_press)
fig.canvas.mpl_connect("motion_notify_event", on_motion)
fig.canvas.mpl_connect("button_release_event", on_release)

plt.show()