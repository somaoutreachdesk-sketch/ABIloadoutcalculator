import numpy as np
import matplotlib.pyplot as plt
import streamlit as st


# ---------- CORE MATH ----------

def break_even_loss(win_rate, avg_win):
    """Break-even average loss per losing raid (negative)."""
    return -(win_rate * avg_win) / (1 - win_rate)


def monte_carlo_sim(win_rate, avg_win, avg_loss, num_raids=1000):
    """Simple Monte Carlo equity simulation."""
    equity = [0]
    for _ in range(num_raids):
        if np.random.random() < win_rate:
            equity.append(equity[-1] + avg_win)
        else:
            equity.append(equity[-1] + avg_loss)
    return equity


# ---------- STREAMLIT APP ----------

st.set_page_config(page_title="ABI Break-Even Loadout Calculator", layout="wide")

st.title("Arena Breakout Infinite – Break-Even Loadout Calculator")

st.markdown(
    "Paste the stats from your **profile overview** page:\n\n"
    "- Total Raids\n"
    "- Extraction Rate (%)\n"
    "- Total Earned (millions of koen)\n\n"
    "The app will calculate your **break-even death cost** and simulate three example loadouts."
)

col_input, col_info = st.columns([1, 1])

with col_input:
    st.subheader("Stats Input")

    total_raids = st.number_input("Total Raids", min_value=1.0, step=1.0)
    extraction_rate_percent = st.number_input(
        "Extraction Rate %", min_value=0.1, max_value=99.9, step=0.1
    )
    total_earned_millions = st.number_input(
        "Total Earned (millions of koen)", min_value=0.01, step=0.1
    )

    run_button = st.button("Calculate & Simulate")

with col_info:
    st.subheader("How to read this")
    st.markdown(
        "- **Break-even loss** = maximum average koen you can lose per death and not "
        "lose money long term.\n"
        "- If your real losing loadout is **cheaper** than break-even → you are "
        "**profitable**.\n"
        "- The simulations show **example** outcomes if your loadout is:\n"
        "  - too expensive (negative expectancy)\n"
        "  - exactly break-even\n"
        "  - cheaper than break-even (profitable)\n"
        "  These are *illustrations*, not exact loadout recommendations.\n"
    )

st.markdown("---")

if run_button:
    p = extraction_rate_percent / 100.0
    total_earned = total_earned_millions * 1_000_000
    wins = total_raids * p

    if wins <= 0:
        st.error("Extraction rate / total raids combo is invalid.")
    else:
        avg_win = total_earned / wins
        L_BE = break_even_loss(p, avg_win)
        abs_L_BE = abs(L_BE)
        rr_be = avg_win / abs_L_BE

        st.subheader("Calculated Stats")
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.metric("Win Rate", f"{p*100:.2f}%")
            st.metric(
                "Average Win",
                f"{avg_win:,.0f} koen ({avg_win/1e6:.2f} M)",
            )

        with col_b:
            st.metric(
                "Break-even Loss",
                f"{L_BE:,.0f} koen ({abs_L_BE/1e6:.2f} M)",
            )
            st.metric("Break-even R:R", f"{rr_be:.2f} : 1")

        with col_c:
            st.markdown(
                "**Rule of thumb:**\n\n"
                f"- If your usual losing loadout is **< {abs_L_BE/1e6:.2f}M**, "
                "you're winning long-term.\n"
                f"- If it's **> {abs_L_BE/1e6:.2f}M**, you're bleeding over time."
            )

        # ---------- PIE + SIMS SIDE BY SIDE ----------

        col_left, col_right = st.columns([1, 2])

        # Pie chart
        with col_left:
            fig1, ax1 = plt.subplots()
            ax1.pie(
                [p, 1 - p],
                labels=["Win (Extract)", "Loss (Death)"],
                autopct="%1.1f%%",
                colors=["green", "red"],
            )
            ax1.set_title("Win vs Loss Rate")
            st.pyplot(fig1)

        # Equity simulations (examples)
        with col_right:
            st.markdown(
                "*The following equity curves are **example simulations** based on your "
                "stats. They illustrate what happens if your average losing loadout is "
                "too expensive, break-even, or efficient relative to your break-even "
                "loss. They are **not exact loadout recommendations**.*"
            )

            loss_bad = -abs_L_BE * 1.5   # example: too expensive
            loss_break = L_BE            # example: break-even
            loss_good = -abs_L_BE * 0.5  # example: efficient/cheap

            eq_bad = monte_carlo_sim(p, avg_win, loss_bad)
            eq_break = monte_carlo_sim(p, avg_win, loss_break)
            eq_good = monte_carlo_sim(p, avg_win, loss_good)

            fig2, ax2 = plt.subplots()
            ax2.plot(
                eq_bad,
                color="red",
                label=f"Example: Too Expensive (≈{abs(loss_bad)/1e6:.2f}M loss)",
            )
            ax2.plot(
                eq_break,
                color="orange",
                label=f"Example: Break-even (≈{abs_L_BE/1e6:.2f}M loss)",
            )
            ax2.plot(
                eq_good,
                color="green",
                label=f"Example: Efficient (≈{abs(loss_good)/1e6:.2f}M loss)",
            )

            ax2.set_title("Equity Curve Simulations (1000 raids)")
            ax2.set_xlabel("Raids")
            ax2.set_ylabel("Total Profit (koen)")
            ax2.grid(True)
            ax2.legend()
            st.pyplot(fig2)

        st.success("Done! Use the break-even loss as your max average losing loadout.")
else:
    st.info("Enter your stats and click **Calculate & Simulate** to see results.")
