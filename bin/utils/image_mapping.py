#!/usr/bin/env python

# Import necessary libraries
import cv2
import numpy as np
import logging
from utils import logging_config
from dipy.align.imwarp import SymmetricDiffeomorphicRegistration
from dipy.align.metrics import CCMetric
from dipy.align.transforms import AffineTransform2D
from dipy.align.imaffine import AffineRegistration

logging_config.setup_logging()
logger = logging.getLogger(__name__)

def compute_diffeomorphic_mapping_dipy(y: np.ndarray, x: np.ndarray, sigma_diff=20, radius=20):
    """
    Compute diffeomorphic mapping using DIPY.
    
    Parameters:
        y (ndarray): Reference image.
        x (ndarray): Moving image to be registered.
        sigma_diff (int, optional): Standard deviation for the CCMetric. Default is 20.
        radius (int, optional): Radius for the CCMetric. Default is 20.

    Returns:
        mapping: A mapping object containing the transformation information.
    """
    if y.shape != x.shape:
        raise ValueError("Reference image (y) and moving image (x) must have the same shape.")
    
    # Initialize the AffineRegistration and AffineTransform2D objects
    affreg = AffineRegistration()
    transform = AffineTransform2D()

    # Perform the optimization procedure with two images reference_image and moving_image
    # params0 is set to None as we don't have initial parameters
    affine = affreg.optimize(y, x, transform, params0=None)

    # Define the metric and registration object
    metric = CCMetric(2, sigma_diff=sigma_diff, radius=radius)
    sdr = SymmetricDiffeomorphicRegistration(metric)

    # Perform the diffeomorphic registration using a pre-alignment from affine registration
    mapping = sdr.optimize(y, x, prealign=affine.affine)

    return mapping 

def compute_affine_mapping_cv2(y: np.ndarray, x: np.ndarray):
    """
    Compute affine mapping using OpenCV.
    
    Parameters:
        y (ndarray): Reference image.
        x (ndarray): Moving image to be registered.

    Returns:
        matrix (ndarray): Affine transformation matrix.
    """    
    # Normalize images to 8-bit (0-255) for feature detection
    y_normalized = cv2.normalize(y, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    x_normalized = cv2.normalize(x, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # Detect ORB keypoints and descriptors
    orb = cv2.ORB_create(
        fastThreshold=0, 
        edgeThreshold=0,
        nfeatures=1000
    )

    keypoints1, descriptors1 = orb.detectAndCompute(y_normalized, None)
    keypoints2, descriptors2 = orb.detectAndCompute(x_normalized, None)

    if descriptors1 is None or descriptors2 is None:
        raise ValueError("One of the descriptors is empty")
    
    # Convert descriptors to uint8 if they are not already in that format
    if descriptors1 is not None and descriptors1.dtype != np.uint8:
        descriptors1 = descriptors1.astype(np.uint8)

    if descriptors2 is not None and descriptors2.dtype != np.uint8:
        descriptors2 = descriptors2.astype(np.uint8)
    
    # Match descriptors using BFMatcher
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)
    matches = sorted(matches, key=lambda x: x.distance)

    # Extract location of good matches
    points1 = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    points2 = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

    # Compute affine transformation matrix
    matrix, mask = cv2.estimateAffinePartial2D(points2, points1)

    return matrix

def apply_mapping(mapping, x, method='dipy'):
    """
    Apply mapping to image.
    
    Parameters:
        mapping: A mapping object from either the DIPY or the OpenCV package.
        x (ndarray): 2-dimensional numpy array to transform.
        method (str, optional): Method used for mapping. Either 'cv2' or 'dipy'. Default is 'dipy'.

    Returns:
        mapped (ndarray): Transformed image as 2D numpy array.
    """
    if method not in ['cv2', 'dipy']:
        raise ValueError("Invalid method specified. Choose either 'cv2' or 'dipy'.")

    if method == 'dipy':
        mapped = mapping.transform(x)
    if method == 'cv2':
        height, width = x.shape[:2]
        mapped = cv2.warpAffine(x, mapping, (width, height))
    
    return mapped
