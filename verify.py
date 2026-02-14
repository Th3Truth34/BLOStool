from src.physics import LinkBudget

def test_link_budget():
    # TestCase 1: 10km LoS
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
    print(f"Is LoS: {res['is_los']}")
    
    # TestCase 2: 100km BRLoS (Obstructed)
    # Earth curvature should block this.
    # d = 4.12 * (sqrt(10) + sqrt(10)) = 4.12 * 6.32 = 26km radio horizon
    lb2 = LinkBudget(
        freq_mhz=2400, bandwidth_mhz=10, dist_km=100, 
        tx_h_m=10, rx_h_m=10, 
        tx_p_dbm=30, tx_g_dbi=0, tx_l_db=0, rx_g_dbi=0, rx_l_db=0, rx_nf_db=0,
        fade_margin_db=0, impl_loss_db=0
    )
    res2 = lb2.run()
    print("\n--- Test Case 2: 100km BRLoS ---")
    print(f"FSPL: {res2['fspl']:.2f} dB")
    print(f"Diffraction Loss: {res2['diffraction_loss']:.2f} dB (Expected > 0)")
    print(f"Is LoS: {res2['is_los']}")

if __name__ == "__main__":
    test_link_budget()
