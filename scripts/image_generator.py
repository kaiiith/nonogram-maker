import numpy as np
from PIL import Image

# finds the dimensions in the range provided that is closest to the original aspect ratio
def approximate_dimensions(ratio, width, width_range):
    best_approx = (0, 0)
    best_approx_error = 1

    # itterates over each width in the provided range
    for i in range(width_range * 2 + 1):

        # checks to ensure the width is not negative or 0
        if (width - width_range + i <= 0):
            continue

        x = width - width_range + i
        y = round(x / ratio)

        # calculates the percentage error of the new aspect ratio compared to the original
        new_ratio = x / y
        error = abs((ratio - new_ratio) / ratio)

        # updates the best approximation if the calculated error is smaller than the current best
        if (error < best_approx_error):
            best_approx = (x, y)
            best_approx_error = error

        # updates the best approximation if the calculated error is the same as the current best,
        # but the current width is closer to the requested width
        elif (error == best_approx_error):
            if (abs(width - x) <= abs(width - best_approx[0])):
                best_approx = (x, y)
                best_approx_error = error
        
    return best_approx
    

def resize_image(img, dimensions):
    img = img.resize(dimensions)
    img_array = np.asarray(img)

    return img_array