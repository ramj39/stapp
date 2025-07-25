import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# --- Page Setup ---
st.set_page_config(page_title="Group Statistics Analyzer", layout="centered")
st.title("🔬 Group Statistics Analyzer")

# --- User Greeting ---
name = st.text_input("Enter your name:")
if name:
    st.success(f"Hello, {name}! Welcome to the app.")

# --- Group Input ---
grps = st.selectbox("How many groups?", [5, 6])
group_data = []

for i in range(1, grps + 1):
    st.subheader(f"📊 Group {i}")
    num = st.number_input(f"How many values in Group {i}?", min_value=1, step=1, key=f"num_{i}")
    values = st.text_area(f"Enter {int(num)} values separated by commas:", key=f"val_{i}")
    
    if values:
        try:
            val_list = [float(v.strip()) for v in values.split(",") if v.strip()]
            if len(val_list) != num:
                st.warning(f"Please enter exactly {int(num)} values.")
            else:
                total = sum(val_list)
                avg = total / len(val_list)
                r = max(val_list) - min(val_list)
                group_data.append({
                    "Group": f"Group {i}",
                    "Values": val_list,
                    "Total": total,
                    "Average": avg,
                    "Range": r
                })
                st.success(f"✅ Group {i} accepted.")
        except ValueError:
            st.error("Please enter valid numbers separated by commas.")

# --- Summary Table & Charts ---
if len(group_data) == grps:
    st.subheader("📋 Group Summary Table")
    df = pd.DataFrame([{
        "Group": g["Group"],
        "Total": f"{g['Total']:.2f}",
        "Average": f"{g['Average']:.2f}",
        "Range": f"{g['Range']:.2f}",
        "Values": ", ".join(f"{v:.2f}" for v in g["Values"])
    } for g in group_data])
    st.dataframe(df)

    # Group Means Plot
    st.subheader("📈 Group Means")
    means = [g["Average"] for g in group_data]
    plt.figure(figsize=(6, 3))
    plt.plot(range(1, grps + 1), means, marker='o', color='blue')
    plt.xlabel("Group Number")
    plt.ylabel("Mean")
    plt.grid(True)
    st.pyplot(plt)

    # Groupwise Value Distribution
    st.subheader("📊 Groupwise Value Distribution")
    plt.figure(figsize=(8, 4))
    for i, g in enumerate(group_data, start=1):
        plt.plot(range(1, len(g["Values"]) + 1), g["Values"], marker='o', label=g["Group"])
    plt.xlabel("Index Within Group")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)

    # Overall Trend With Control Limits
    st.subheader("📊 Overall Trend With Control Limits")
    all_values = []
    all_indices = []
    idx = 1
    for g in group_data:
        all_values.extend(g["Values"])
        all_indices.extend(range(idx, idx + len(g["Values"])))
        idx += len(g["Values"])

    plt.figure(figsize=(10, 4))
    plt.plot(all_indices, all_values, color='purple', marker='o', linestyle='-', label='Values')
    LCL = st.number_input("Enter LCL:")
    UCL = st.number_input("Enter UCL:")
    if LCL and UCL:
        plt.axhline(UCL, color='red', linestyle='--', label='UCL')
        plt.axhline(LCL, color='green', linestyle='--', label='LCL')
    plt.xlabel("Cumulative Index")
    plt.ylabel("Value")
    plt.title("Trend Line With Control Limits")
    plt.grid(True)
    plt.xticks(all_indices)
    plt.yticks(sorted(set([round(v, 2) for v in all_values + [LCL, UCL]])))
    plt.legend()
    st.pyplot(plt)

    # --- Capability Analysis ---
    st.subheader("📐 Capability Analysis")
    ranges = [g["Range"] for g in group_data]
    range_avg = sum(ranges) / grps
    means = [g["Average"] for g in group_data]
    mbar = sum(means) / grps

    d2_constants = {
        2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326, 6: 2.534,
        7: 2.704, 8: 2.847, 9: 2.970, 10: 3.078
    }

    subgroup_size = st.number_input("Subgroup Size", min_value=2, max_value=25, value=grps)
    d2_value = d2_constants.get(subgroup_size)

    if d2_value:
        sd = range_avg / d2_value
        st.markdown(f"**Mean of group means (m̄):** `{mbar:.2f}`")
        st.markdown(f"**Average range (R̄):** `{range_avg:.2f}`")
        st.markdown(f"**Estimated standard deviation (σ):** `{sd:.4f}`")

        num_controls = st.number_input("How many control charts?", min_value=1, step=1, key="num_controls_key")
        for i in range(int(num_controls)):
            lcl = st.number_input(f"LCL for control {i+1}", key=f"lcl_{i}")
            ucl = st.number_input(f"UCL for control {i+1}", key=f"ucl_{i}")
            if lcl and ucl:
                cpl = (mbar - lcl) / (3 * sd)
                cpu = (ucl - mbar) / (3 * sd)
                cpk = min(cpl, cpu)
                st.markdown(f"### Control Chart {i+1}")
                st.markdown(f"**LCL:** `{lcl:.2f}` **UCL:** `{ucl:.2f}`")
                st.markdown(f"**CPL:** `{cpl:.2f}` **CPU:** `{cpu:.2f}` **CPK:** `{cpk:.2f}` — {'✅ Good' if cpk >= 1.6 else '⚠️ Needs improvement'}")
    else:
        st.error("⚠️ d₂ constant not found for this subgroup size.")

# --- Visitor Counter ---
counter_file = "visitor_count.txt"

def get_visitor_count():
    try:
        if not os.path.exists(counter_file):
            with open(counter_file, "w") as f:
                f.write("1")
            return 1
        else:
            with open(counter_file, "r+") as f:
                count = int(f.read().strip() or 0) + 1
                f.seek(0)
                f.write(str(count))
                return count
    except Exception as e:
        st.error(f"Counter error: {e}")
        return "N/A"

visitor_count = get_visitor_count()
st.markdown("---")
st.markdown("[STREAMLIT SQC APP](app by Subramanian Ramajayam)")
st.markdown(f"👀 **App visits so far:** `{visitor_count}`")
