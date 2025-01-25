import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from obspy import read, Stream, Trace
from io import BytesIO
from sklearn.metrics import r2_score

st.set_page_config(page_title="Seismic Fractal Dimension", page_icon="📈")

# Sidebar information
st.sidebar.title("Instructions")
st.sidebar.markdown("""
1. Upload a seismogram file (SAC, MSEED, etc.)
2. Preview data and adjust parameters
3. Click 'Calculate Fractal Dimension'
4. Download results as PNG
""")

st.sidebar.markdown("### Example File")
if st.sidebar.button("Generate Synthetic Test Signal"):
    np.random.seed(42)
    n_points = 1000
    t = np.linspace(0, 100, n_points)
    y = np.cumsum(np.random.randn(n_points))  # Brownian motion
    
    header = {
        'network': 'SY',
        'station': 'FRAC', 
        'location': '00',
        'channel': 'FD1',
        'delta': t[1]-t[0]
    }
    
    synthetic_stream = Stream([Trace(data=y, header=header)])
    buf = BytesIO()
    synthetic_stream.write(buf, format='SAC')
    st.sidebar.download_button("Download Synthetic Test Signal", buf.getvalue(), "SY.FRAC.00.FD1.sac")

def try_read_seismic(file_buffer):
    try:
        st = read(file_buffer)
        return 'obspy', st
    except Exception:
        return None, None

def calculate_fractal_dimension(t, y, epsilons):
    t_range = np.ptp(t) + 1e-12
    y_range = np.ptp(y) + 1e-12
    
    t_norm = (t - t.min()) / t_range
    y_norm = (y - y.min()) / y_range
    
    log_counts, log_scales = [], []
    
    for eps in epsilons:
        if eps < 1e-10:
            continue
        
        bx = np.floor(t_norm / eps).astype(int)
        by = np.floor(y_norm / eps).astype(int)
        boxes = set(zip(bx, by))
        
        if len(boxes) > 1:  # Require at least 2 boxes for meaningful slope
            log_scales.append(np.log(1/eps))
            log_counts.append(np.log(len(boxes)))
    
    if len(log_scales) < 2:
        return None, None, None
    
    slope, intercept = np.polyfit(log_scales, log_counts, 1)
    y_pred = slope * np.array(log_scales) + intercept
    r2 = r2_score(log_counts, y_pred)
    return slope, (log_scales, log_counts), r2

# Main app
st.title("Fractal Dimension Calculator for Seismic Signals")

uploaded_file = st.file_uploader("Upload seismic file", type=None,
                                help="Supported formats: SAC, MSEED, etc.")

if uploaded_file:
    file_buffer = BytesIO(uploaded_file.getvalue())
    format_type, stream = try_read_seismic(file_buffer)

    if format_type == 'obspy':
        st.subheader("Trace Information")
        st.write(stream)
        
        st.subheader("Waveform Visualization")
        fig = plt.figure(figsize=(10, 4))
        stream.plot(fig=fig)
        st.pyplot(fig)

        with st.expander("Advanced Settings"):
            st.markdown("### Preprocessing")
            col1, col2 = st.columns(2)
            detrend_type = col1.selectbox("Detrend method", ["none", "linear", "demean"])
            filter_type = col2.selectbox("Filter type", ["none", "lowpass", "highpass", "bandpass"])
            
            freq_min, freq_max = None, None
            if filter_type != "none":
                if filter_type in ["lowpass", "bandpass"]:
                    freq_max = col1.number_input("Max frequency (Hz)", value=1.0, min_value=0.1)
                if filter_type in ["highpass", "bandpass"]:
                    freq_min = col2.number_input("Min frequency (Hz)", value=0.1, min_value=0.01)
            
            st.markdown("### Box-Counting Parameters")
            col1, col2, col3 = st.columns(3)
            max_eps = col1.number_input("Max box size", value=0.5, min_value=0.01, max_value=1.0)
            min_eps = col2.number_input("Min box size", value=0.001, min_value=0.0001, max_value=0.1)
            num_eps = col3.number_input("Number of steps", value=20, min_value=5)
            
            if min_eps >= max_eps:
                st.error("Min box size must be smaller than max box size!")
                st.stop()

        if st.button("Calculate Fractal Dimension"):
            with st.spinner("Calculating..."):
                try:
                    results = []
                    plot_buffers = []
                    epsilons = np.logspace(np.log10(max_eps), np.log10(min_eps), num_eps)
                    
                    for tr in stream:
                        tr_processed = tr.copy()
                        if detrend_type != "none":
                            tr_processed.detrend(type=detrend_type)
                        if filter_type != "none":
                            if filter_type == "lowpass":
                                tr_processed.filter('lowpass', freq=freq_max)
                            elif filter_type == "highpass":
                                tr_processed.filter('highpass', freq=freq_min)
                            elif filter_type == "bandpass":
                                tr_processed.filter('bandpass', freqmin=freq_min, freqmax=freq_max)
                        
                        t = tr_processed.times()
                        y = tr_processed.data
                        fd, (log_scales, log_counts), r2 = calculate_fractal_dimension(t, y, epsilons)
                        
                        if fd is None:
                            st.warning(f"Could not compute FD for {tr.id} - insufficient valid boxes.")
                            continue
                        
                        # Plotting
                        fig, ax = plt.subplots()
                        ax.scatter(log_scales, log_counts, c='r', edgecolor='k', label='Data')
                        fit_line = np.poly1d([fd, np.mean(log_counts) - fd * np.mean(log_scales)])(log_scales)
                        ax.plot(log_scales, fit_line, 'k--', 
                                label=f'Fit: D = {fd:.3f}\nR² = {r2:.3f}')
                        ax.set_xlabel("log(1/ε)")
                        ax.set_ylabel("log(N(ε))")
                        ax.grid(True, which='both', linestyle='--', alpha=0.7)
                        ax.legend()
                        
                        buf = BytesIO()
                        fig.savefig(buf, format="png", bbox_inches='tight')
                        plot_buffers.append(buf)
                        plt.close(fig)
                        
                        results.append({
                            'id': tr_processed.id,
                            'fd': fd,
                            'r2': r2,
                            'log_scales': log_scales,
                            'log_counts': log_counts
                        })
                    
                    st.subheader("Results")
                    for idx, result in enumerate(results):
                        with st.expander(f"{result['id']} - FD: {result['fd']:.3f} (R²={result['r2']:.3f})", expanded=True):
                            col1, col2 = st.columns([1, 2])
                            col1.markdown(f"""
                            **Fractal Dimension**  
                            `{result['fd']:.4f}`  
                            **R² (Fit Quality)**  
                            `{result['r2']:.4f}`  
                            **Trace ID**  
                            `{result['id']}`
                            """)
                            col2.image(plot_buffers[idx].getvalue(), 
                                     caption=f"Log-Log Plot for {result['id']}")
                            st.download_button(
                                label=f"Download Plot - {result['id']}",
                                data=plot_buffers[idx].getvalue(),
                                file_name=f"fractal_{result['id'].replace(',', '_')}.png",
                                mime="image/png",
                                key=f"dl_{idx}"
                            )
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.error("Unsupported file format. Hex preview:")
        file_buffer.seek(0)
        hex_data = file_buffer.read(256).hex()
        st.text(' '.join(hex_data[i:i+2] for i in range(0, len(hex_data), 2)))
else:
    st.info("📂 Please upload a seismic file or use the synthetic example in the sidebar.")