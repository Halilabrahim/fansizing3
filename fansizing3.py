import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import math
import tempfile
import os

st.set_page_config(page_title="Aircraft Fan Selection Wizard")
st.title("🧠 Aircraft Fan Selection Wizard ✈️")

# -------------------------
# Fan Database (simplified)
# -------------------------
fan_database = [
    {"brand": "ebm-papst", "model": "A2D200-AA02-01", "type": "Axial", "max_flow": 800, "max_pressure": 350, "power": 70, "voltage": 12, "rpm": 2500, "width": 120, "height": 120, "depth": 38},
    {"brand": "Sanyo Denki", "model": "9HV1248P1G03", "type": "Centrifugal", "max_flow": 420, "max_pressure": 500, "power": 48, "voltage": 12, "rpm": 3200, "width": 92, "height": 92, "depth": 38},
    {"brand": "Delta", "model": "AFB1212GHE", "type": "Axial", "max_flow": 600, "max_pressure": 300, "power": 60, "voltage": 12, "rpm": 4000, "width": 120, "height": 120, "depth": 25},
    {"brand": "Nidec", "model": "U76X12MS1A5-57", "type": "Mixed", "max_flow": 500, "max_pressure": 400, "power": 55, "voltage": 12, "rpm": 2800, "width": 76, "height": 76, "depth": 38},
    {"brand": "ebm-papst", "model": "R2E220-AA40-17", "type": "Centrifugal", "max_flow": 1000, "max_pressure": 600, "power": 120, "voltage": 12, "rpm": 1800, "width": 220, "height": 220, "depth": 100},
    {"brand": "Delta", "model": "BFB1012VH", "type": "Centrifugal", "max_flow": 300, "max_pressure": 450, "power": 40, "voltage": 12, "rpm": 3500, "width": 97, "height": 97, "depth": 33},
]

if "step" not in st.session_state:
    st.session_state.step = 1

if st.session_state.step == 1:
    st.header("Step 1: Use Case Definition")
    region = st.selectbox("Select Aircraft Region", ["Cabin", "Cockpit", "Avionics Bay", "Cargo Hold", "Lavatory", "Galley"])
    purpose = st.radio("What is the fan used for?", ["Cooling", "Ventilation", "Exhaust", "Electronic Equipment"])
    critical = st.radio("Is this a critical system?", ["Yes", "No"])
    if st.button("Next"):
        st.session_state.region = region
        st.session_state.purpose = purpose
        st.session_state.critical = critical
        st.session_state.step += 1

elif st.session_state.step == 2:
    st.header("Step 2: Performance Requirements")
    flow_rate_input = st.number_input("Required Flow Rate (in m³/h)", value=500)
    pressure_drop_input = st.number_input("Estimated Pressure Drop (Pa)", value=250)
    efficiency_input = st.slider("Fan Efficiency (%)", 30, 90, 60)
    rpm_input = st.number_input("Desired Fan RPM", value=2500)
    num_fans = st.number_input("Number of Fans", min_value=1, value=1)
    if st.button("Next"):
        st.session_state.flow_rate = flow_rate_input
        st.session_state.pressure_drop = pressure_drop_input
        st.session_state.efficiency = efficiency_input
        st.session_state.rpm = rpm_input
        st.session_state.num_fans = num_fans
        st.session_state.step += 1
    if st.button("Back"):
        st.session_state.step -= 1

elif st.session_state.step == 3:
    st.header("Step 3: Electrical & Mechanical Constraints")
    voltage_input = st.number_input("Operating Voltage (VDC)", value=12)
    width_input = st.number_input("Max Width (mm)", value=120)
    height_input = st.number_input("Max Height (mm)", value=120)
    depth_input = st.number_input("Max Depth (mm)", value=40)
    if st.button("Next"):
        st.session_state.voltage = voltage_input
        st.session_state.width = width_input
        st.session_state.height = height_input
        st.session_state.depth = depth_input
        st.session_state.step += 1
    if st.button("Back"):
        st.session_state.step -= 1

elif st.session_state.step == 4:
    st.header("Step 4: Fan Selection Results")

    flow_rate_m3s = st.session_state.flow_rate / 3600
    efficiency_decimal = st.session_state.efficiency / 100
    power_watt = (flow_rate_m3s * st.session_state.pressure_drop) / efficiency_decimal
    total_power = power_watt * st.session_state.num_fans

    st.markdown(f"**Calculated Power per Fan:** {power_watt:.2f} W")
    st.markdown(f"**Total System Power:** {total_power:.2f} W")

    matches = []
    for fan in fan_database:
        if (fan["max_flow"] >= st.session_state.flow_rate and
            fan["max_pressure"] >= st.session_state.pressure_drop and
            fan["voltage"] == st.session_state.voltage and
            abs(fan["rpm"] - st.session_state.rpm) <= 1000 and
            fan["width"] <= st.session_state.width and
            fan["height"] <= st.session_state.height and
            fan["depth"] <= st.session_state.depth):
            matches.append(fan)

    st.subheader("🔧 Suitable Fan Models")
    if matches:
        df = pd.DataFrame(matches)
        st.dataframe(df)

        # Graph - Pressure vs Flow
        st.subheader("📉 Example Fan Curve")
        flow_vals = [0, st.session_state.flow_rate]
        pressure_vals = [st.session_state.pressure_drop, 0]
        fig, ax = plt.subplots()
        ax.plot(flow_vals, pressure_vals, label="Estimated Curve")
        ax.set_xlabel("Flow Rate (m³/h)")
        ax.set_ylabel("Static Pressure (Pa)")
        ax.set_title("Pressure vs Flow")
        ax.grid(True)
        st.pyplot(fig)

        # PDF Export
        if st.button("📄 Export PDF Report"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Aircraft Fan Selection Report", ln=True, align='C')
            pdf.ln(10)
            pdf.cell(200, 10, txt=f"Region: {st.session_state.region}", ln=True)
            pdf.cell(200, 10, txt=f"Purpose: {st.session_state.purpose}", ln=True)
            pdf.cell(200, 10, txt=f"Critical: {st.session_state.critical}", ln=True)
            pdf.cell(200, 10, txt=f"Flow: {st.session_state.flow_rate} m³/h", ln=True)
            pdf.cell(200, 10, txt=f"Pressure Drop: {st.session_state.pressure_drop} Pa", ln=True)
            pdf.cell(200, 10, txt=f"Efficiency: {st.session_state.efficiency}%", ln=True)
            pdf.cell(200, 10, txt=f"Voltage: {st.session_state.voltage} VDC", ln=True)
            pdf.cell(200, 10, txt=f"Calculated Power per Fan: {power_watt:.2f} W", ln=True)
            pdf.cell(200, 10, txt=f"Total Power: {total_power:.2f} W", ln=True)
            pdf.ln(10)
            for fan in matches:
                pdf.cell(200, 10, txt=f"{fan['brand']} – {fan['model']}", ln=True)
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            pdf.output(tmp_file.name)
            with open(tmp_file.name, "rb") as f:
                st.download_button("Download PDF", f, file_name="fan_selection_report.pdf")
            os.unlink(tmp_file.name)
    else:
        st.warning("No suitable fan found based on your input parameters.")

    if st.button("Back"):
        st.session_state.step -= 1

st.caption("Designed for aircraft fan selection | Halil İbrahim Aydın ✈️")
