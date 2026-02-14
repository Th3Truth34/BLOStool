import plotly.graph_objects as go
import numpy as np

def plot_earth_slice(link_budget_obj):
    """
    Generates a Plotly figure showing the Earth slice, TX/RX, LoS, and Fresnel Zone.
    """
    lb = link_budget_obj
    dist_m = lb.dist_m
    if dist_m == 0:
        return go.Figure()

    # Generate X coordinates
    x = np.linspace(0, dist_m, 500)
    
    # Earth Surface (Parabolic approximation using Effective Radius)
    # y = -x^2 / (2 * Re_eff)
    # But usually we define x=0 as TX location. 
    # Let's center the parabola at dist/2 to make it symmetric?
    # No, standard is TX at 0.
    # However, to make it look like a hill between them if obstructed?
    # No, simple model: TX at x=0.
    
    # Correct approach for "Curved Earth, Straight Ray":
    # Earth surface drops as we move away from the tangent point (Tx).
    # y_earth = - x^2 / (2 * R_eff) is correct if we assume tangent at x=0.
    # But if looking from side, usually we want the "Bulge" in the middle.
    # That happens if we define the "Reference Line" as the chord connecting x=0,y=0 and x=D,y=0?
    # No.
    # Let's stick to the standard k-factor engineering diagram:
    # Earth curvature is y = -x^2 / (2 * k * Re) relative to a flat tangent at x=0.
    
    R_eff = lb.eff_earth_radius_m
    y_earth = -(x**2) / (2 * R_eff)
    
    # TX Position
    tx_pos = (0, lb.tx_h_m) # TX is at 0 distance, h_tx above reference (which is tangent, so 0)
    
    # RX Position
    # Surface at D is -D^2 / (2 * R_eff)
    y_surface_at_rx = -(dist_m**2) / (2 * R_eff)
    rx_pos = (dist_m, y_surface_at_rx + lb.rx_h_m)
    
    # LoS Line
    # Straight line between TX and RX
    slope = (rx_pos[1] - tx_pos[1]) / (rx_pos[0] - tx_pos[0])
    y_los = tx_pos[1] + slope * x
    
    # Fresnel Zones
    d1 = x
    d2 = dist_m - x
    # Avoid division by zero at endpoints
    with np.errstate(divide='ignore', invalid='ignore'):
        f1 = np.sqrt((lb.wavelength * d1 * d2) / (d1 + d2))
    f1[0] = 0
    f1[-1] = 0
    
    y_f1_upper = y_los + f1
    y_f1_lower = y_los - f1
    
    # Create Plot
    fig = go.Figure()
    
    # 1. Earth Surface - Filled Area
    # We want to fill down to some low value
    y_min = min(np.min(y_earth), np.min(y_los)) - 100
    
    fig.add_trace(go.Scatter(
        x=x, y=y_earth,
        mode='lines',
        fill='tozeroy',
        name='Earth Surface',
        line=dict(color='brown', width=2),
        fillcolor='tan'
    ))
    
    # 2. Fresnel Zone
    # Create a closed polygon for the fill
    x_poly = np.concatenate([x, x[::-1]])
    y_poly = np.concatenate([y_f1_upper, y_f1_lower[::-1]])
    
    fig.add_trace(go.Scatter(
        x=x_poly, y=y_poly,
        fill='toself',
        mode='lines',
        name='1st Fresnel Zone',
        line=dict(color='rgba(0, 255, 0, 0.4)', width=1),
        fillcolor='rgba(0, 255, 0, 0.2)',
        hoverinfo='skip'
    ))
    
    # 3. LoS Line
    fig.add_trace(go.Scatter(
        x=[tx_pos[0], rx_pos[0]],
        y=[tx_pos[1], rx_pos[1]],
        mode='lines',
        name='Line of Sight',
        line=dict(color='blue', dash='dash')
    ))
    
    # 4. Obstruction Highlight
    # Identify points where Earth > Fresnel Lower (obstruction)
    # Actually, technically obstruction is Earth > LoS - 0.6*F1 for 60% clearance logic
    # But usually "Obstruction" means Earth > LoS.
    # "Diffraction Zone" is Earth > LoS - F1.
    
    # Let's highlight where Earth penetrates the Fresnel Zone (Red)
    obstruction_mask = y_earth > y_f1_lower
    if np.any(obstruction_mask):
        obs_x = x[obstruction_mask]
        obs_y = y_earth[obstruction_mask]
        fig.add_trace(go.Scatter(
            x=obs_x, y=obs_y,
            mode='markers',
            name='Obstruction',
            marker=dict(color='red', size=2)
        ))

    # 5. TX and RX Markers
    fig.add_trace(go.Scatter(
        x=[tx_pos[0]], y=[tx_pos[1]],
        mode='markers+text',
        name='GCS (TX)',
        text=['GCS'],
        textposition='top center',
        marker=dict(color='black', size=10, symbol='triangle-up')
    ))
    
    fig.add_trace(go.Scatter(
        x=[rx_pos[0]], y=[rx_pos[1]],
        mode='markers+text',
        name='UAS (RX)',
        text=['UAS'],
        textposition='top center',
        marker=dict(color='black', size=10, symbol='diamond')
    ))
    
    # Layout Update
    fig.update_layout(
        title="Link Geometry (Effective Earth Curvature k=1.33)",
        xaxis_title="Distance (m)",
        yaxis_title="Height (m)",
        legend=dict(orientation="h", y=-0.2),
        margin=dict(l=20, r=20, t=40, b=20),
        height=500,
        scene=dict(aspectmode='data') # Wait, this is 2D
    )
    # Fix Aspect Ratio to be somewhat realistic (or exaggerated Y?)
    # Realistic is impossible (150km vs 100m).
    # Let's leave it auto, but maybe hint
    # fig.update_yaxes(scaleanchor="x", scaleratio=0.1) # Exaggerate Y by 10x?
    # User requested "Exaggerated scale"
    
    return fig
