from copyreg import remove_extension
from fileinput import filename
import os
import numpy as np
from PIL import Image
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from image_generator import *

# disable the toolbar
mpl.rcParams['toolbar'] = 'None'

is_mouse_down = False
current_mouse_pos = (0, 0)
paint_colour = True

# find the name of the first image in the directory
image_name = ''
for file in os.listdir():
    if file.endswith(('.png', '.jpeg', '.jpg')):
        image_name = file
        break

# open the image and convert it to grayscale
raw_img = Image.open(image_name)
raw_img_grayscale = raw_img.convert('L')

# find the aspect ratio and calculate the best size to set the puzzle
width, height = raw_img.size
aspect_ratio = width / height
width, height = approximate_dimensions(aspect_ratio, 21, 5)

# create the figure and set a gid for the plot
fig, ax = plt.subplots()
ax.set_gid('A')

# define the properties of the sliders and buttons
ax_threshold = plt.axes([0.2, 0.01, 0.6, 0.03])
threshold_slider = Slider(ax_threshold, 'threshold', 0, 255, valinit=128, valstep=1)
ax_size = plt.axes([0.01, 0.1, 0.03, 0.8])
size_slider = Slider(ax_size, 'size', 5, 50, valinit=width, valstep=1, orientation="vertical")
ax_save = plt.axes([0.89, 0.01, 0.1, 0.05])
save_button = Button(ax_save, 'Save')


# reapplies the formatting of the plot after it is redrawn
def modifyPlot():
    dimensions = img_array_bw.shape
    ax.set_title("{}x{}".format(dimensions[1], dimensions[0]))
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.set_xticks([])
    ax.set_yticks([])

# called whenever the threshold slider is moved
def updateThreshold(threshold):
    global img_array_bw

    # clears the current image
    ax.cla()

    # turns the grayscale image into black/white based on a threshold
    img_array_bw = np.greater(img_array, threshold)

    # display the image
    ax.imshow(img_array_bw, cmap='gray')
    modifyPlot()
    fig.canvas.draw_idle()

# called whenever the size slider is moved
def updateSize(size):
    global img_array

    # find the new width and height, then resize the image
    width, height = approximate_dimensions(aspect_ratio, size, 0)
    img_array = resize_image(raw_img_grayscale, (width, height))

    # call updateThreshold() to turn the grayscale to black/white and redraw the frame
    updateThreshold(threshold_slider.val)

# saves the current image to disk
def save(val):
    prefixsuffix = image_name.split('.')
    im = Image.fromarray(img_array_bw)
    im.save("{}_nonogram.{}".format(prefixsuffix[0], prefixsuffix[1]))

# called whenever a mouse button is pressed
def onClick(event):
    global current_mouse_pos
    global is_mouse_down
    global paint_colour

    # check if left mouse button was pressed
    if event.button == 1:
        try:
            # make sure the image was clicked and not a slider
            if event.inaxes.get_gid() == 'A':
                is_mouse_down = True
                current_mouse_pos = (event.xdata, event.ydata)

                # round the mouse coords to integers
                x = round(event.xdata)
                y = round(event.ydata)

                # set if the user will be painting black or white
                paint_colour = not img_array_bw[y][x]

                onMove(event)
        except AttributeError: # only the image subplot has a get_gid() function, so an
            return             # AttributeError will be thrown if anywhere else is clicked

# called when a mouse button is released
def onRelease(event):
    global is_mouse_down

    # we only care about left mouse button
    if event.button == 1:
        is_mouse_down = False

# called whenever the mouse moves
def onMove(event):
    global current_mouse_pos

    if is_mouse_down:
        try:
            # round the mouse coords to integers
            x = round(event.xdata)
            y = round(event.ydata)

            # if the mouse is over a different pixel to before, change the colour and update location
            if (x, y) != current_mouse_pos:
                img_array_bw[y][x] = paint_colour

                current_mouse_pos = (x, y)

        except TypeError:     # if the mouse isn't over the image, event.x/ydata returns none,
            return            # which doesn't define round()
        except IndexError:  # mousing over either slider changes x or y to the slider value,
            return          # which is often larger than the bounds of the image

        # clear the screen and update the image
        ax.cla()
        ax.imshow(img_array_bw, cmap='gray')
        modifyPlot()
        fig.canvas.draw_idle()


# declare the functions to be called when the sliders are moved or buttons pressed
threshold_slider.on_changed(updateThreshold)
size_slider.on_changed(updateSize)
save_button.on_clicked(save)

# declare the functions to be called on mouse events
cid = fig.canvas.mpl_connect('button_press_event', onClick)
rid = fig.canvas.mpl_connect('button_release_event', onRelease)
mid = fig.canvas.mpl_connect('motion_notify_event', onMove)

# call updateSize to draw the initial image
updateSize(width)

# set the title of the window and show it
plt.get_current_fig_manager().set_window_title('nonogram maker')
plt.show()