import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.ticker import FuncFormatter


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

# -------- DISCLAIMER --------
st.warning(
    "**Disclaimer:**\n"
    "- Results only reflect your **past performance**, so the model cannot predict how different gear or a new playstyle will affect your break-even value.\n"
    "- From my experience, while better gear can help, the survival gains are usually **small relative to the increased loadout value**.\n"
    "- Also from experience, **playstyle and context** (solo vs squad, aggressive vs careful) tend to have a **much larger impact** on survival than loadout value.\n"
    "- The model is intentionally **simple** because ABI does **not provide detailed per-raid data**, limiting the precision of any calculation.\n"
    "- Consider the break-even loadout a **reference point**, not advice on what to run.\n"
)

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
        "- **Break-even loss** = the maximum average koen you can lose per death and "
        "still break even long-term.\n"
        "- **R:R (Risk-to-Reward)** = how much you win per successful extract compared "
        "to how much you lose per death.\n"
        "  - Example: **2.0 : 1** means your average win is **2× bigger** than your "
        "average losing loadout.\n"
        "- If your real losing loadout is **cheaper** than break-even → you are "
        "**profitable** over many raids.\n"
        "- The simulations show **example outcomes** of running:\n"
        "  - too expensive loadouts (negative expectancy)\n"
        "  - break-even loadouts (neutral expectancy)\n"
        "  - efficient loadouts (positive expectancy)\n"
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
                "Break-even Losing Loadout Value",
                f"{abs_L_BE:,.0f} koen ({abs_L_BE/1e6:.2f} M)",
            )
            st.metric("Break-even R:R", f"{rr_be:.2f} : 1")

        with col_c:
            st.markdown(
                "**Rule of thumb:**\n\n"
                f"- If your losing loadout is **< {abs_L_BE/1e6:.2f}M**, "
                "you’re profitable long-term.\n"
                f"- If it’s **> {abs_L_BE/1e6:.2f}M**, you slowly bleed money.\n"
            )

        # ---------- PIE + SIMS SIDE BY SIDE ----------

        col_left, col_right = st.columns([1, 2])

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

        with col_right:

            # ---- CHART CLARIFICATION ----
            st.info(
                "**Note:** The loadouts shown below (Too Expensive / Break-even / Efficient) "
                "are **illustrative examples**, not recommended kits. Any loadout above "
                "your break-even value loses money long-term, and any loadout below it "
                "is profitable."
            )

            loadout_expensive = abs_L_BE * 1.5
            loadout_break_even = abs_L_BE
            loadout_efficient = abs_L_BE * 0.5

            loss_bad = -loadout_expensive
            loss_break = -loadout_break_even
            loss_good = -loadout_efficient

            eq_bad = monte_carlo_sim(p, avg_win, loss_bad)
            eq_break = monte_carlo_sim(p, avg_win, loss_break)
            eq_good = monte_carlo_sim(p, avg_win, loss_good)

            fig2, ax2 = plt.subplots()

            # --- CLEAN MILLION FORMAT ---
            def millions_formatter(x, pos):
                return f"{x/1e6:.0f}M"
            ax2.yaxis.set_major_formatter(FuncFormatter(millions_formatter))

            ax2.plot(
                eq_bad,
                color="red",
                label=f"Too Expensive Loadout (≈{loadout_expensive/1e6:.2f}M koen)",
            )
            ax2.plot(
                eq_break,
                color="orange",
                label=f"Break-even Loadout (≈{loadout_break_even/1e6:.2f}M koen)",
            )
            ax2.plot(
                eq_good,
                color="green",
                label=f"Efficient Loadout (≈{loadout_efficient/1e6:.2f}M koen)",
            )

            ax2.set_title("Example Equity Curve Simulations (1000 raids)")
            ax2.set_xlabel("Raids")
            ax2.set_ylabel("Total Profit (M koen)")
            ax2.grid(True)
            ax2.legend()
            st.pyplot(fig2)

        st.success("Done! Use the break-even loadout value as your max losing loadout.")

else:
    st.info("Enter your stats and click **Calculate & Simulate** to see results.")
