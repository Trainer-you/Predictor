import streamlit as st
import pandas as pd

st.set_page_config(page_title="Teen Patti Smart Predictor", layout="centered")
st.title("🃏 Teen Patti Chair Predictor (Advanced Logic)")
st.markdown("Uses pattern rules, win streaks, and pot sizes to predict likely winners")

if "rounds" not in st.session_state:
    st.session_state.rounds = []

chairs = ["A", "B", "C"]

# Input form
with st.form("round_input"):
    st.subheader("➕ Add Round Data")
    pot_a = st.number_input("Pot A (in thousands)", min_value=0, step=1)
    pot_b = st.number_input("Pot B (in thousands)", min_value=0, step=1)
    pot_c = st.number_input("Pot C (in thousands)", min_value=0, step=1)
    winner = st.selectbox("Winning Chair", chairs)
    submit = st.form_submit_button("Add Round")

if submit:
    st.session_state.rounds.append({"Round": len(st.session_state.rounds)+1, "A": pot_a, "B": pot_b, "C": pot_c, "Winner": winner})
    st.success(f"✅ Round {len(st.session_state.rounds)} added")

# Show data
if st.session_state.rounds:
    df = pd.DataFrame(st.session_state.rounds)
    st.subheader("📜 Match History (Last 10)")
    st.dataframe(df.tail(10), use_container_width=True)

    # Smart rule-based prediction
    def advanced_predictor(df, lookback=10):
        recent = df.tail(lookback)
        win_counts = recent["Winner"].value_counts()
        last_winner = recent.iloc[-1]["Winner"]
        second_last_winner = recent.iloc[-2]["Winner"] if len(recent) >= 2 else None

        scores = {chair: 0 for chair in chairs}
        reasons = {chair: [] for chair in chairs}

        for chair in scores:
            no_win_boost = 5 - recent["Winner"].tolist().count(chair)
            scores[chair] += no_win_boost
            reasons[chair].append(f"+{no_win_boost} for fewer recent wins")

            if chair == last_winner and chair == second_last_winner:
                scores[chair] -= 2
                reasons[chair].append("-2 for possible over-win penalty")

            if len(recent) >= 3:
                last_3 = recent["Winner"].tolist()[-3:]
                if last_3 == ['A', 'B', 'C'] and chair == 'A':
                    scores[chair] += 3
                    reasons[chair].append("+3 for A\u2192B\u2192C\u2192A pattern")
                elif last_3 == ['B', 'C', 'A'] and chair == 'B':
                    scores[chair] += 3
                    reasons[chair].append("+3 for B\u2192C\u2192A\u2192B pattern")
                elif last_3 == ['C', 'A', 'B'] and chair == 'C':
                    scores[chair] += 3
                    reasons[chair].append("+3 for C\u2192A\u2192B\u2192C pattern")

            last_pots = recent.iloc[-1][["A", "B", "C"]]
            chair_pot = recent.iloc[-1][chair]
            if chair_pot == min(last_pots):
                scores[chair] += 2
                reasons[chair].append("+2 for lowest pot last round")
            elif chair_pot == sorted(last_pots)[1]:
                scores[chair] += 1
                reasons[chair].append("+1 for medium pot last round")

        return scores, reasons

    scores, reasons = advanced_predictor(df)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    st.subheader("🔮 Prediction for Next Round")
    for idx, (chair, score) in enumerate(sorted_scores[:2], start=1):
        st.markdown(f"**{idx}. Chair {chair}** — Score: `{score}`")
        with st.expander(f"📌 Reasoning for Chair {chair}"):
            for reason in reasons[chair]:
                st.markdown(f"- {reason}")
else:
    st.info("Please enter at least 1 round to start predictions.")
