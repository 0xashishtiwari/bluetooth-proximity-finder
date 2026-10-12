import math

def estimate_distance(rssi: float , reference_rssi:float = -50 , 
                      path_loss_exponent : float = 2.0) -> float :
    """Estimate distance in meters using the log-distance path-loss model."""
    if not math.isfinite(rssi):
        raise ValueError("RSSI must be a finite number.")
    
    if not math.isfinite(path_loss_exponent) or path_loss_exponent <= 0:
        raise ValueError("Path loss exponent must be a positive finite number.")

    exponent = (reference_rssi - rssi) / (10  * path_loss_exponent)
    return 10 ** exponent