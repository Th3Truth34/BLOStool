import streamlit as st
import numpy as np
import pandas as pd
from src.physics import LinkBudget
from src.visualization import plot_earth_slice

st.set_page_config(page_title="UAS Link Budget Calculator", layout="wide")

st.title("🛰️ UAS Link Budget Calculator (0-150km)")
st.markdown("""
**"Napkin Math to Flight Ready"**: Accurate LoS and BRLoS modeling with Earth curvature and diffraction.
""")

# Sidebar
st.sidebar.header("System Configuration")

# RF Parameters
st.sidebar.subheader("RF Parameters")
freq = st.sidebar.number_input("Frequency (MHz)", value=2400.0, step=100.0)
bw = st.sidebar.number_input("Bandwidth (MHz)", value=10.0, step=1.0)
tx_p_dbm = st.sidebar.number_input("TX Power (dBm)", value=30.0, step=1.0)
tx_g_dbi = st.sidebar.number_input("TX Antenna Gain (dBi)", value=5.0, step=0.5)
tx_l_db = st.sidebar.number_input("TX Cable Loss (dB)", value=1.0, step=0.1)
rx_g_dbi = st.sidebar.number_input("RX Antenna Gain (dBi)", value=5.0, step=0.5)
rx_l_db = st.sidebar.number_input("RX Cable Loss (dB)", value=1.0, step=0.1)
rx_nf_db = st.sidebar.number_input("RX Noise Figure (dB)", value=4.0, step=0.5)

# Geometry
st.sidebar.subheader("Geometry")
dist_km = st.sidebar.slider("Link Distance (km)", 0.1, 150.0, 10.0, step=0.1)
gcs_h = st.sidebar.number_input("GCS Height (m AGL)", value=10.0, step=1.0)
drone_h = st.sidebar.number_input("Drone Height (m AGL)", value=100.0, step=10.0)

# Environment
st.sidebar.subheader("Environment")
fade_margin = st.sidebar.number_input("Fade Margin (dB)", value=10.0, step=1.0)
impl_loss = st.sidebar.number_input("Implementation Loss (dB)", value=2.0, step=0.5)

# Calculation
lb = LinkBudget(freq, bw, dist_km, gcs_h, drone_h, 
                tx_p_dbm, tx_g_dbi, tx_l_db, rx_g_dbi, rx_l_db, rx_nf_db,
                fade_margin, impl_loss)

results = lb.run()

# Metrics Row
col1, col2, col3, col4 = st.columns(4)

rsl = results['rsl']
snr = results['snr']
link_margin = snr - abs(results['noise_floor']) # Wait, Margin is RSL - Sensitivity?
# Or simpler: Margin = SNR_achieved - SNR_required
# But we don't have a single SNR required, we have a table.
# Let's show "Fade Margin" relative to QPSK limit? No.
# Standard Link Margin usually implies Margin above Sensitivity.
# Let's define sensitivity as Thermal Noise + NF + Required SNR for lowest rate (QPSK ~6dB).
sensitivity = results['noise_floor'] + 6.0
margin_at_lowest_rate = rsl - sensitivity

# Color coding
def color_metric(val, lower, upper, inverse=False):
    if inverse:
        if val < lower: return "normal"
        if val < upper: return "off"
        return "inverse"
    else:
        if val > upper: return "normal"
        if val > lower: return "off" 
        return "inverse" 

# RSL Color
rsl_delta = ""
if rsl > -75:
    rsl_color = "green"
elif rsl > -85:
    rsl_color = "orange"
else:
    rsl_color = "red"

col1.metric("RSL (Received Signal Level)", f"{rsl:.1f} dBm", delta=None)
# Streamlit metric coloring logic is limited to delta, let's use markdown for custom color if needed
# But metric is fine.

col2.metric("Link Margin (vs QPSK)", f"{margin_at_lowest_rate:.1f} dB", delta_color="normal" if margin_at_lowest_rate > 10 else "off")

col3.metric("Throughput (Est)", f"{results['throughput_mbps']:.1f} Mbps", f"{results['modulation']}")

col4.metric("Path Loss (Total)", f"{results['total_loss']:.1f} dB", help=f"FSPL: {results['fspl']:.1f} dB, Diffraction: {results['diffraction_loss']:.1f} dB")

# Warning Banners
if not results['is_los']:
    st.error(f"⚠️ **Obstructed Line of Sight!** Diffraction Loss: {results['diffraction_loss']:.1f} dB")
elif results['is_los'] and results['min_clearance'] < results['f1_at_obstruction'] * 0.6:
     st.warning("⚠️ **Fresnel Zone Encroachment.** Clearance < 60% F1.")
else:
    st.success("✅ **Clear Line of Sight**")

# Visualization
st.subheader("Earth Slice Visualization")
fig = plot_earth_slice(lb)
st.plotly_chart(fig, use_container_width=True)

# Detailed Data Table
with st.expander("Detailed Link Budget Breakdown"):
    data = {
        "Parameter": [
            "Frequency", "Distance", "Free Space Path Loss", "Diffraction Loss", 
            "Total Path Loss", "TX Power", "Total Gain (TX+RX)", "Implementation Loss", 
            "Fade Margin", "Received Signal Level (RSL)", "Thermal Noise Floor", 
            "SNR", "Modulation"
        ],
        "Value": [
            f"{freq} MHz", f"{dist_km} km", f"{results['fspl']:.2f} dB", f"{results['diffraction_loss']:.2f} dB",
            f"{results['total_loss']:.2f} dB", f"{tx_p_dbm} dBm", f"{tx_g_dbi + rx_g_dbi} dBi", f"{impl_loss} dB",
            f"{fade_margin} dB", f"{rsl:.2f} dBm", f"{results['noise_floor']:.2f} dBm",
            f"{snr:.2f} dB", results['modulation']
        ]
    }
    st.table(pd.DataFrame(data))

# Instructions
st.info("""
**How to use:**
1. Adjust Frequency and Bandwidth.
2. Set TX/RX parameters (Power, Gains).
3. Use the **Distance** slider to move the drone away.
4. Watch the **Earth Slice** plot to see when the drone drops below the horizon (red obstruction).
5. Observe the **Throughput** drop as SNR decreases due to diffraction loss.
""")
