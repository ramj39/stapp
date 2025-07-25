import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Group Statistics Analyzer", layout="centered")
st.title("🔬 Group Statistics Analyzer")

# User input
name = st.text_input("Enter your name:")
if name:
    st.success(f"Hello, {name}! Welcome to the app.")

grps = st.selectbox("How many groups?", [5, 6])
group_data = []

# Collect group data
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

# Display table and plots
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

    # Line chart of group means
    st.subheader("📈 Group Means")
    means = [g["Average"] for g in group_data]
    plt.figure(figsize=(6, 3))
    plt.plot(range(1, grps + 1), means, marker='o', color='blue')
    plt.xlabel("Group Number")
    plt.ylabel("Mean")
    plt.grid(True)
    st.pyplot(plt)

    # Line chart of all values
    st.subheader("📊 Groupwise Value Distribution")
    plt.figure(figsize=(8, 4))
    for i, g in enumerate(group_data, start=1):
        plt.plot(range(1, len(g["Values"]) + 1), g["Values"], marker='o', label=g["Group"])
    plt.xlabel("Index Within Group")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)

    # Capability metrics
    st.subheader("📐 Capability Analysis")
    ranges = [g["Range"] for g in group_data]
    range_avg = sum(ranges) / grps
    sd = range_avg / 2.33
    mbar = sum(means) / grps

    LCL = st.number_input("Enter LCL:")
    UCL = st.number_input("Enter UCL:")

    if LCL and UCL:
        cpl = (mbar - LCL) / (3 * sd)
        cpu = (UCL - mbar) / (3 * sd)
        cpk = min(cpl, cpu)

        st.markdown(f"**Mean of group means (m̄):** `{mbar:.2f}`")
        st.markdown(f"**Estimated SD:** `{sd:.2f}`")
        st.markdown(f"**CPL:** `{cpl:.2f}`")
        st.markdown(f"**CPU:** `{cpu:.2f}`")
        st.markdown(f"**CPK:** `{cpk:.2f}` — {'✅ Good' if cpk >= 1.6 else '⚠️ Needs improvement'}")
        input()
