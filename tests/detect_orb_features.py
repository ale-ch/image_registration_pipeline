def detect_orb_features(img1, img2, initial_features=2000, max_features=10000):
    """
    Detect ORB features with adaptive feature count and proper error handling.
    
    Args:
        img1, img2: Input images
        initial_features: Starting number of features to detect
        max_features: Maximum number of features to attempt
    
    Returns:
        tuple: (keypoints1, descriptors1, keypoints2, descriptors2) or None if failed
    """
    # Validate inputs
    if img1 is None or img2 is None:
        raise ValueError("Input images cannot be None")
    
    if not isinstance(img1, np.ndarray) or not isinstance(img2, np.ndarray):
        raise ValueError("Inputs must be numpy arrays")
        
    n_features = initial_features
    
    while n_features <= max_features:
        # Create ORB detector with reasonable defaults
        orb = cv2.ORB_create(
            nfeatures=n_features,
            fastThreshold=0, 
            edgeThreshold=0
        )
        
        try:
            # Detect and compute features
            keypoints1, descriptors1 = orb.detectAndCompute(img1, None)
            keypoints2, descriptors2 = orb.detectAndCompute(img2, None)
            
            # Check if we got enough features
            min_features = 10  # Minimum useful number of features
            if (descriptors1 is not None and descriptors2 is not None and 
                len(keypoints1) >= min_features and len(keypoints2) >= min_features):
                print(f"Successfully detected features: {len(keypoints1)} and {len(keypoints2)}")
                return keypoints1, descriptors1, keypoints2, descriptors2
                
        except cv2.error as e:
            print(f"OpenCV error: {e}")
            return None
            
        print(f"Insufficient features found, increasing from {n_features} to {n_features + 500}")
        n_features += 500
    
    print("Failed to detect sufficient features even at maximum setting")
    return None