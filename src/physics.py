import numpy as np

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

    def calculate_radio_horizon(self):
        """Radio horizon distances for each terminal and total.
        Returns (d_h1_m, d_h2_m, d_h_total_m)."""
        d_h1 = np.sqrt(2 * self.eff_earth_radius_m * self.tx_h_m)
        d_h2 = np.sqrt(2 * self.eff_earth_radius_m * self.rx_h_m)
        return d_h1, d_h2, d_h1 + d_h2

    def _smooth_earth_diffraction(self):
        """ITU-R P.526-15 Section 4.3: Smooth spherical Earth diffraction.
        Assumes beta ~ 1 (valid for UHF frequencies > 20 MHz over land).
        Returns diffraction loss in dB (positive value)."""
        a_e = self.eff_earth_radius_m
        lam = self.wavelength
        d = self.dist_m

        # Normalized distance
        X = d * (np.pi / (lam * a_e**2)) ** (1.0 / 3.0)

        # Normalized antenna heights
        height_factor = (np.pi**2 / (lam**2 * a_e)) ** (1.0 / 3.0)
        Y1 = 2.0 * self.tx_h_m * height_factor
        Y2 = 2.0 * self.rx_h_m * height_factor

        # Distance attenuation F(X)
        # Deep shadow formula valid for X >= 1.6
        # For transition region (X < 1.6), linearly interpolate from 0 at X=0
        if X >= 1.6:
            F_X = 11.0 + 10.0 * np.log10(X) - 17.6 * X
        else:
            # F at X=1.6
            F_at_boundary = 11.0 + 10.0 * np.log10(1.6) - 17.6 * 1.6
            F_X = F_at_boundary * (X / 1.6)

        # Height-gain functions G(Y)
        def height_gain(Y):
            if Y > 2.0:
                return 17.6 * np.sqrt(Y - 1.1) - 5.0 * np.log10(Y - 1.1) - 8.0
            elif Y > 0:
                return 20.0 * np.log10(Y + 0.1 * Y**3)
            else:
                return -100.0  # antenna at ground level

        G_Y1 = height_gain(Y1)
        G_Y2 = height_gain(Y2)

        # Total diffraction loss: L = -F(X) - G(Y1) - G(Y2)
        loss_db = -F_X - G_Y1 - G_Y2
        return max(loss_db, 0.0)

    def calculate_diffraction_loss(self):
        """Calculate diffraction loss due to earth curvature.
        Uses knife-edge for LoS/near-LoS paths, smooth-earth (ITU-R P.526-15)
        for beyond-radio-horizon paths."""
        # Clearance geometry (used for visualization and LoS determination)
        steps = 1000
        d_vec = np.linspace(0, self.dist_m, steps)

        # Earth bulge relative to chord connecting TX and RX surface positions
        h_bulge_vec = (d_vec * (self.dist_m - d_vec)) / (2 * self.eff_earth_radius_m)

        # LOS ray height (flat earth + bulge model)
        slope = (self.rx_h_m - self.tx_h_m) / self.dist_m
        h_ray_vec = self.tx_h_m + slope * d_vec

        # Clearance = Ray Height - Earth Bulge
        clearance_vec = h_ray_vec - h_bulge_vec

        # Find minimum clearance (exclude endpoints)
        valid_indices = slice(1, -1)
        if steps < 3:
             valid_indices = slice(0, steps)

        clearance_to_check = clearance_vec[valid_indices]
        d_to_check = d_vec[valid_indices]

        min_clearance_idx_local = np.argmin(clearance_to_check)
        min_clearance = clearance_to_check[min_clearance_idx_local]
        d_obstruction = d_to_check[min_clearance_idx_local]

        # Fresnel radius at worst point
        f1 = self.calculate_fresnel_radius(d_obstruction)

        # Determine diffraction model based on radio horizon
        _, _, d_horizon_total = self.calculate_radio_horizon()

        if self.dist_m > d_horizon_total:
            # BRLoS: use ITU-R P.526 smooth-earth diffraction
            loss_db = self._smooth_earth_diffraction()
        else:
            # LoS / near-LoS: use knife-edge for Fresnel encroachment
            if f1 == 0:
                v_param = -100
            else:
                v_param = -1 * min_clearance * np.sqrt(2) / f1

            # ITU-R P.526-15 knife-edge approximation
            if v_param > -0.7:
                 loss_db = 6.9 + 20 * np.log10(
                     np.sqrt((v_param - 0.1)**2 + 1) + v_param - 0.1)
            else:
                 loss_db = 0.0
            loss_db = max(loss_db, 0.0)

        return loss_db, min_clearance, f1, d_obstruction

    def calculate_thermal_noise(self):
        """Thermal Noise Floor (dBm) = -174 + 10*log10(BW_Hz) + NF"""
        return -174 + 10 * np.log10(self.bandwidth_mhz * 1e6) + self.rx_nf_db

    def run(self):
        fspl = self.calculate_fspl()
        diff_loss, min_clearance, f1_at_obstruction, d_obstruction = self.calculate_diffraction_loss()

        total_loss = fspl + diff_loss + self.tx_l_db + self.rx_l_db + self.impl_loss_db + self.fade_margin_db
        total_gain = self.tx_g_dbi + self.rx_g_dbi

        rsl = self.tx_p_dbm + total_gain - total_loss

        noise_floor = self.calculate_thermal_noise()
        snr_db = rsl - noise_floor

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

        _, _, d_horizon_total = self.calculate_radio_horizon()

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
            "is_los": min_clearance > 0,
            "d_horizon_km": d_horizon_total / 1000.0,
        }
