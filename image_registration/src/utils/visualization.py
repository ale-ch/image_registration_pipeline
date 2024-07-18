import matplotlib.pyplot as plt
import numpy as np

def grouped_scatter(data, group, x_col, y_col, figsize: tuple =(8, 6), crop: tuple = ()):
    # Scatter plot x and y colored by group
    plt.figure(figsize=figsize)

    if crop:
        plt.xlim(crop[0], crop[1])
        plt.ylim(crop[2], crop[3])

    for g in data[group].unique():
        subset = data[data[group] == g]
        plt.scatter(subset[x_col], subset[y_col], label=g)

    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.legend(title=group)
    plt.show()


def plot_images_row(images, titles=[], ncols=3, figsize=(12, 4), cmap='gray', alpha=1):
    # Function to plot a row of images
    nrows = 1
    fig, axs = plt.subplots(nrows, ncols, figsize=figsize)
    axs = np.array([axs]) if ncols == 1 else axs  # Ensure axs is always 2D

    for i, ax in enumerate(axs.flatten()):
        if i < len(images):
            ax.imshow(images[i], cmap=cmap, alpha=alpha)  # Adjust cmap based on image type (e.g., 'gray' for grayscale)
            ax.axis('off')

            if len(titles):
                ax.set_title(titles[i])
        else:
            ax.axis('off')  # Hide extra subplots

    plt.tight_layout()
    plt.show()


def create_stereo_image(img1, img2, shape):
    """
    Arguments:
    shape: tuple of shape (k, m, 3)
    """
    
    stereo = np.zeros(shape, dtype=np.uint8)
    stereo[..., 0] = img1
    stereo[..., 1] = img2

    return stereo