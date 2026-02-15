from src.physics import LinkBudget

def test_link_budget():
    # TestCase 1: 10km LoS (well within radio horizon)
    lb = LinkBudget(
        freq_mhz=2400, bandwidth_mhz=10, dist_km=10,
        tx_h_m=10, rx_h_m=100,
        tx_p_dbm=30, tx_g_dbi=0, tx_l_db=0, rx_g_dbi=0, rx_l_db=0, rx_nf_db=0,
        fade_margin_db=0, impl_loss_db=0
    )
    res = lb.run()
    print("--- Test Case 1: 10km LoS ---")
    print(f"FSPL: {res['fspl']:.2f} dB (Expected ~120 dB)")
    print(f"Diffraction Loss: {res['diffraction_loss']:.2f} dB (Expected 0 dB)")
    print(f"Radio Horizon: {res['d_horizon_km']:.1f} km")
    print(f"Is LoS: {res['is_los']}")

    # TestCase 2: 100km BRLoS at 2.4 GHz (deeply obstructed)
    # Radio horizon at 10m/10m ~ 26 km, so 100 km is way beyond
    lb2 = LinkBudget(
        freq_mhz=2400, bandwidth_mhz=10, dist_km=100,
        tx_h_m=10, rx_h_m=10,
        tx_p_dbm=30, tx_g_dbi=0, tx_l_db=0, rx_g_dbi=0, rx_l_db=0, rx_nf_db=0,
        fade_margin_db=0, impl_loss_db=0
    )
    res2 = lb2.run()
    print("\n--- Test Case 2: 100km BRLoS (2.4 GHz, 10m/10m) ---")
    print(f"FSPL: {res2['fspl']:.2f} dB")
    print(f"Diffraction Loss: {res2['diffraction_loss']:.2f} dB (smooth-earth, expected >> knife-edge)")
    print(f"Radio Horizon: {res2['d_horizon_km']:.1f} km")
    print(f"Is LoS: {res2['is_los']}")
    print(f"SNR: {res2['snr']:.2f} dB")
    print(f"Modulation: {res2['modulation']}")

    # TestCase 3: Default scenario (414 MHz, 100km, 10m/100m)
    # Hand calc: diffraction ~ 51 dB, RSL ~ -133 dBm, No Link
    lb3 = LinkBudget(
        freq_mhz=414, bandwidth_mhz=5, dist_km=100,
        tx_h_m=10, rx_h_m=100,
        tx_p_dbm=50, tx_g_dbi=5, tx_l_db=1, rx_g_dbi=1.5, rx_l_db=1, rx_nf_db=4,
        fade_margin_db=10, impl_loss_db=2
    )
    res3 = lb3.run()
    print("\n--- Test Case 3: Default BRLoS (414 MHz, 100km, 10m/100m) ---")
    print(f"FSPL: {res3['fspl']:.2f} dB (hand: 124.79)")
    print(f"Diffraction Loss: {res3['diffraction_loss']:.2f} dB (hand: ~51.0)")
    print(f"Radio Horizon: {res3['d_horizon_km']:.1f} km (hand: 54.2)")
    print(f"Total Loss: {res3['total_loss']:.2f} dB (hand: ~189.8)")
    print(f"RSL: {res3['rsl']:.2f} dBm (hand: ~-133.3)")
    print(f"SNR: {res3['snr']:.2f} dB (hand: ~-30.3)")
    print(f"Modulation: {res3['modulation']} (hand: No Link)")

    # TestCase 4: Near radio horizon (54 km, should be near transition)
    lb4 = LinkBudget(
        freq_mhz=414, bandwidth_mhz=5, dist_km=54,
        tx_h_m=10, rx_h_m=100,
        tx_p_dbm=50, tx_g_dbi=5, tx_l_db=1, rx_g_dbi=1.5, rx_l_db=1, rx_nf_db=4,
        fade_margin_db=10, impl_loss_db=2
    )
    res4 = lb4.run()
    print("\n--- Test Case 4: Near Radio Horizon (54 km) ---")
    print(f"Radio Horizon: {res4['d_horizon_km']:.1f} km")
    print(f"Diffraction Loss: {res4['diffraction_loss']:.2f} dB")
    print(f"Is LoS: {res4['is_los']}")
    print(f"SNR: {res4['snr']:.2f} dB")
    print(f"Modulation: {res4['modulation']}")

if __name__ == "__main__":
    test_link_budget()
