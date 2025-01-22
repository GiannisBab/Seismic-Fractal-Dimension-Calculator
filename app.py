import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from obspy import read, Stream
from io import BytesIO

st.set_page_config(page_title="Seismic Fractal Dimension")

# Sidebar information
st.sidebar.title("Instructions")
st.sidebar.markdown("""
1. Upload a seismogram file (SAC, MSEED, etc.)
2. Preview data and adjust parameters
3. Click 'Calculate Fractal Dimension'
4. Download results as CSV/PNG
""")

st.sidebar.markdown("### Example File")
st.sidebar.markdown("Download sample SAC file from [IRIS](https://ds.iris.edu/files/sac-examples/)")

def try_read_seismic(file_buffer):
    """Simplified reader using only ObsPy's automatic detection"""
    try:
        st = read(file_buffer)
        return 'obspy', st
    except Exception:
        return None, None

def calculate_fractal_dimension(t, y, epsilons):
    """Calculate box-counting fractal dimension"""
    t_range = np.ptp(t) + 1e-12
    y_range = np.ptp(y) + 1e-12
    
    t_norm = (t - t.min()) / t_range
    y_norm = (y - y.min()) / y_range
    
    log_counts = []
    log_scales = []
    
    for eps in epsilons:
        if eps < 1e-10:
            continue
        
        bx = np.floor(t_norm / eps).astype(int)
        by = np.floor(y_norm / eps).astype(int)
        
        boxes = set(zip(bx, by))
        if len(boxes) == 0:
            continue
            
        log_scales.append(np.log(1/eps))
        log_counts.append(np.log(len(boxes)))
    
    if len(log_scales) < 2:
        return None, None
    
    slope, _ = np.polyfit(log_scales, log_counts, 1)
    return slope, (log_scales, log_counts)

# Main app
st.title("Fractal Dimension Calculator for Seismic Signals")

uploaded_file = st.file_uploader("Upload seismic file", type=None,
                                help="Supported formats: SAC, MSEED, etc.")

if uploaded_file:
    file_buffer = BytesIO(uploaded_file.getvalue())
    file_size = len(uploaded_file.getvalue())
    
    format_type, stream = try_read_seismic(file_buffer)

    if format_type == 'obspy':
        tr = stream[0]  # Use first trace
        
        # Trace information
        st.subheader("Trace Information")
        st.write(stream)
        
        # Updated waveform visualization
        st.subheader("Waveform Visualization")
        fig = plt.figure(figsize=(10, 4))
        stream.plot(fig=fig)
        st.pyplot(fig)

        # Advanced parameters and processing
        with st.expander("Advanced Settings"):
            st.markdown("### Preprocessing")
            col1, col2 = st.columns(2)
            
            detrend_type = col1.selectbox("Detrend method",
                                         ["none", "linear", "demean"])
            
            filter_type = col2.selectbox("Filter type",
                                        ["none", "lowpass", "highpass", "bandpass"])
            freq_min, freq_max = None, None
            if filter_type != "none":
                if filter_type in ["lowpass", "bandpass"]:
                    freq_max = col1.number_input("Max frequency (Hz)", 
                                                value=1.0, min_value=0.1)
                if filter_type in ["highpass", "bandpass"]:
                    freq_min = col2.number_input("Min frequency (Hz)", 
                                                value=0.1, min_value=0.01)
            
            st.markdown("### Box-Counting Parameters")
            col1, col2, col3 = st.columns(3)
            max_eps = col1.number_input("Max box size", value=0.5, 
                                       min_value=0.01, max_value=1.0)
            min_eps = col2.number_input("Min box size", value=0.001, 
                                       min_value=0.0001, max_value=0.1)
            num_eps = col3.number_input("Number of steps", 
                                       value=20, min_value=5)

        # Preprocessing
        if detrend_type != "none":
            tr.detrend(type=detrend_type)
            
        if filter_type != "none":
            if filter_type == "lowpass":
                tr.filter('lowpass', freq=freq_max)
            elif filter_type == "highpass":
                tr.filter('highpass', freq=freq_min)
            elif filter_type == "bandpass":
                tr.filter('bandpass', freqmin=freq_min, freqmax=freq_max)

        # Generate epsilon values
        epsilons = np.logspace(np.log10(max_eps), np.log10(min_eps), num_eps)
        
        if st.button("Calculate Fractal Dimension"):
            with st.spinner("Calculating..."):
                try:
                    t = tr.times()
                    y = tr.data
                    
                    fd, (log_scales, log_counts) = calculate_fractal_dimension(t, y, epsilons)
                    
                    if fd is None:
                        st.error("Not enough points for calculation")
                    else:
                        st.subheader(f"Fractal Dimension: **{fd:.4f}**")
                        
                        # Create log-log plot
                        fig2 = plt.figure()
                        plt.scatter(log_scales, log_counts, c='r', edgecolor='k')
                        plt.plot(log_scales, np.poly1d([fd, np.mean(log_counts)-fd*np.mean(log_scales)])(log_scales),
                                'k--', label=f'Fit (D={fd:.3f})')
                        plt.xlabel("log(1/ε)")
                        plt.ylabel("log(N)")
                        plt.legend()
                        st.pyplot(fig2)
                        
                        # Prepare downloads
                        csv = pd.DataFrame({
                            "log_scale": log_scales,
                            "log_count": log_counts
                        }).to_csv(index=False).encode()
                        
                        buf = BytesIO()
                        fig2.savefig(buf, format="png")
                        
                        col1, col2 = st.columns(2)
                        col1.download_button("Download CSV", csv,
                                            "fractal_dimension.csv",
                                            "text/csv")
                        col2.download_button("Download Plot", buf.getvalue(),
                                            "fractal_plot.png",
                                            "image/png")
                except Exception as e:
                    st.error(f"Calculation error: {str(e)}")

    else:
        st.error("Could not identify file format. Displaying hex preview:")
        file_buffer.seek(0)
        hex_data = file_buffer.read(256).hex()
        st.text(' '.join(hex_data[i:i+2] for i in range(0, len(hex_data), 2)))

else:
    st.info("📂Please upload a seismic data file to begin")