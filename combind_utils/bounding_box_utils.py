def read_bounding_box(filename):
    """
    Read a configuration file and extract the bounding box information.
    
    Args:
        filename (str): Path to the input file
        
    Returns:
        dict: Dictionary containing inner and outer box dimensions
    """
    bounding_box = {}
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            parts = line.split()
            if len(parts) < 2:
                continue
                
            key = parts[0]
            value = parts[1]
            
            if key == "INNERBOX":
                bounding_box["inner_box"] = [float(x) for x in value.split(',')]
            elif key == "OUTERBOX":
                bounding_box["outer_box"] = [float(x) for x in value.split(',')]
            elif key == "GRID_CENTER":
                bounding_box["center"] = [float(x) for x in value.split(',')]
                
    return bounding_box
def is_within_bounding_box(coordinate, bounding_box, box_type="outer_box"):
    """
    Check if a 3D coordinate is within the specified bounding box.
    
    Args:
        coordinate (list): [x, y, z] coordinate to check
        bounding_box (dict): Dictionary containing bounding box information
        box_type (str): Which box to check against ("inner_box" or "outer_box")
        
    Returns:
        bool: True if coordinate is within the box, False otherwise
    """
    if box_type not in bounding_box or "center" not in bounding_box:
        raise ValueError(f"Required box information not found in bounding box data")
    
    box_dims = bounding_box[box_type]
    center = bounding_box["center"]
    
    # Check if coordinate is within the box centered at center with dimensions box_dims
    x, y, z = coordinate
    cx, cy, cz = center
    dx, dy, dz = box_dims
    
    # Calculate half-dimensions
    half_dx, half_dy, half_dz = dx/2, dy/2, dz/2
    
    # Check if point is within bounds
    return (cx - half_dx <= x <= cx + half_dx and 
            cy - half_dy <= y <= cy + half_dy and 
            cz - half_dz <= z <= cz + half_dz)