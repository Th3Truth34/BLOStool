import numpy as np
from scipy.special import fresnel

class LinkBudget:
    def __init__(self, freq_mhz, bandwidth_mhz, dist_km, tx_h_m, rx_h_m, 
                 tx_p_dbm, tx_g_dbi, tx_l_db, rx_g_dbi, rx_l_db, rx_nf_db,
                 fade_margin_db=10.0, impl_loss_db=0.0):
        self.freq_mhz = freq_mhz
        self.freq_hz = freq_mhz * 1e6
        self.bandwidth_mhz = bandwidth_mhz
        self.dist_km = dist_km
        self.dist_m = dist_km * 1000
        self.tx_h_m = tx_h_m
        self.rx_h_m = rx_h_m
        self.tx_p_dbm = tx_p_dbm
        self.tx_g_dbi = tx_g_dbi
        self.tx_l_db = tx_l_db
        self.rx_g_dbi = rx_g_dbi
        self.rx_l_db = rx_l_db
        self.rx_nf_db = rx_nf_db
        self.fade_margin_db = fade_margin_db
        self.impl_loss_db = impl_loss_db
        
        # Constants
        self.c = 3e8
        self.k_factor = 1.33  # Standard 4/3 earth
        self.earth_radius_km = 6371.0
        self.eff_earth_radius_m = self.k_factor * self.earth_radius_km * 1000
        
        self.wavelength = self.c / self.freq_hz

    def calculate_fspl(self):
        """Free Space Path Loss in dB."""
        return 20 * np.log10(self.dist_m) + 20 * np.log10(self.freq_hz) - 147.55

    def calculate_fresnel_radius(self, d1_m):
        """Calculate 1st Fresnel Zone radius at distance d1 from TX."""
        if d1_m <= 0 or d1_m >= self.dist_m:
            return 0.0
        d2_m = self.dist_m - d1_m
        return np.sqrt((self.wavelength * d1_m * d2_m) / (d1_m + d2_m))

    def calculate_earth_height(self, d_m):
        """Height of earth bulge at distance d_m, relative to chord between TX and RX base."""
        # This is a simplification. For the plotting, we'll map to a circle.
        # For diffraction, we care about the height of the obstruction (bulge) relative to the LOS line.
        # h = d^2 / (2 * R_eff)
        # Using the parabolic approximation for small angles/distances
        return (d_m**2) / (2 * self.eff_earth_radius_m)

    def calculate_diffraction_loss(self):
        """
        Calculate knife-edge diffraction loss due to earth curvature.
        We approximate the earth as a single knife-edge at the point of maximum obstruction.
        """
        # Point of max bulge is roughly halfway if heights are equal, but moves if they differ.
        # However, for simplifying "Napkin Math", let's find the max obstruction point.
        # The LOS line height at distance d: h_los(d) = h_tx + (h_rx - h_tx) * (d / total_dist)
        # The Earth height at distance d (relative to chord): h_earth(d) = d * (total_dist - d) / (2 * R_eff)
        # Wait, the h_earth formulation above d^2/2R is for drop from tangent.
        # The bulge height relative to the chord connecting 0 and dist is: h = d1*d2 / (2*R_eff).
        
        # We need to find the max value of (h_earth(d) - h_los_relative_to_surface(d))?
        # Actually, let's define the clearance. 
        # h_tx and h_rx are AGL. 
        # Total height at distance d = h_earth_surface(d) + h_agl(d).
        # We want to check clearance between the LOS line and the Earth sphere.
        
        # Let's discretize to find the worst clearance
        steps = 1000
        d_vec = np.linspace(0, self.dist_m, steps)
        
        # Earth bulge height relative to the straight line chord connecting surface at TX and surface at RX
        # h_bulge = (d * (D - d)) / (2 * R_e_eff)
        h_bulge_vec = (d_vec * (self.dist_m - d_vec)) / (2 * self.eff_earth_radius_m)
        
        # Line of Sight height relative to the chord connecting the bases of TX and RX towers
        # But wait, the "chord" goes through the earth. 
        # Let's stick to the "Flat Earth with Bulge" model which is standard for this.
        # The terrain height is the Bulge.
        # The ray height is the straight line between (0, h_tx) and (D, h_rx).
        
        slope = (self.rx_h_m - self.tx_h_m) / self.dist_m
        h_ray_vec = self.tx_h_m + slope * d_vec
        
        # Clearance = Ray Height - Earth Bulge
        clearance_vec = h_ray_vec - h_bulge_vec
        
        # Find minimum clearance (most obstructed point)
        # Exclude endpoints where f1 is 0 and clearance is just antenna height
        valid_indices = slice(1, -1)
        
        # If steps is too small, fallback
        if steps < 3:
             valid_indices = slice(0, steps)
             
        clearance_to_check = clearance_vec[valid_indices]
        d_to_check = d_vec[valid_indices]
        
        min_clearance_idx_local = np.argmin(clearance_to_check)
        min_clearance = clearance_to_check[min_clearance_idx_local]
        d_obstruction = d_to_check[min_clearance_idx_local]
        
        # Calculate Fresnel radius at that point
        f1 = self.calculate_fresnel_radius(d_obstruction)
        
        if f1 == 0:
            v_param = -100 # Effectively clear
        else:
            # v = -h * sqrt(2) / f1  (sign convention: negative h means obstruction? wait)
            # ITU recommendation: v = h \sqrt{2 / (\lambda d1 d2 / D)} = h * \sqrt{2} / F1
            # Here h is the clearance. Positive clearance is good. Negative clearance is obstruction.
            # Usually v is defined such that negative v is clear, positive v is obstructed. 
            # Lee: v = - clearance * sqrt(2) / f1
            v_param = -1 * min_clearance * np.sqrt(2) / f1

        # Diffraction Loss formula J(v)
        # ITU-R P.526-15 Approximation for single knife-edge
        if v_param > -0.7:
             loss_db = 6.9 + 20 * np.log10(np.sqrt((v_param - 0.1)**2 + 1) + v_param - 0.1)
        else:
             loss_db = 0.0
             
        # J(v) should not be negative
        return max(loss_db, 0.0), min_clearance, f1, d_obstruction

    def calculate_thermal_noise(self):
        # Thermal Noise Floor (dBm) = -174 + 10*log10(BW_Hz) + NF
        return -174 + 10 * np.log10(self.bandwidth_mhz * 1e6) + self.rx_nf_db

    def run(self):
        fspl = self.calculate_fspl()
        diff_loss, min_clearance, f1_at_obstruction, d_obstruction = self.calculate_diffraction_loss()
        
        total_loss = fspl + diff_loss + self.tx_l_db + self.rx_l_db + self.impl_loss_db + self.fade_margin_db
        total_gain = self.tx_g_dbi + self.rx_g_dbi
        
        rsl = self.tx_p_dbm + total_gain - total_loss
        
        noise_floor = self.calculate_thermal_noise()
        snr_db = rsl - noise_floor
        
        # Data Rate lookup (Approximate, based on Shannon or typical receiver specs)
        # Using a simplified table for demo
        mcs_table = [
            (-100, "No Link", 0),
            (6, "QPSK 1/2", 6.5),   # Min SNR for QPSK
            (10, "16QAM 1/2", 19.5),
            (15, "16QAM 3/4", 26.0),
            (20, "64QAM 2/3", 58.5),
            (25, "64QAM 3/4", 65.0),
            (30, "256QAM 3/4", 78.0)
        ]
        
        est_throughput = 0
        modulation = "Link Down"
        
        # Scaling throughput by bandwidth (assuming table is for ~10-20MHz, let's normalize to Hz/sec roughly)
        # Actually simplest is just simple efficiency bits/s/Hz
        # QPSK 1/2 = 1 bit/s/Hz
        # 16QAM 1/2 = 2 bits/s/Hz
        # ...
        
        spectral_eff = 0
        if snr_db < 6:
            modulation = "No Link"
        elif snr_db < 10:
            modulation = "QPSK 1/2"
            spectral_eff = 1.0
        elif snr_db < 15:
            modulation = "16QAM 1/2"
            spectral_eff = 2.0
        elif snr_db < 20:
            modulation = "16QAM 3/4"
            spectral_eff = 3.0
        elif snr_db < 25:
            modulation = "64QAM 2/3"
            spectral_eff = 4.0
        elif snr_db < 30:
            modulation = "64QAM 3/4"
            spectral_eff = 4.5
        else:
            modulation = "256QAM"
            spectral_eff = 6.0
            
        est_throughput = spectral_eff * self.bandwidth_mhz
        
        return {
            "fspl": fspl,
            "diffraction_loss": diff_loss,
            "total_loss": total_loss,
            "rsl": rsl,
            "noise_floor": noise_floor,
            "snr": snr_db,
            "min_clearance": min_clearance,
            "f1_at_obstruction": f1_at_obstruction,
            "d_obstruction": d_obstruction,
            "throughput_mbps": est_throughput,
            "modulation": modulation,
            "is_los": min_clearance > 0 # Simple check, technically LoS requires clearance > 0.6 F1 usually
        }
