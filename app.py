import streamlit as st
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="12-Week Fitness Coach", page_icon="💪", layout="centered")
st.title("💪 12-Week Fitness Coach")
st.caption("Mobile-first • 3 sessions/week • 50' per session • Dark-ready")

# ---------- Embedded weekly plan (giữ như cũ) ----------
weekly_schedule = ["Monday", "Wednesday", "Friday"]
focuses = ["Strength + Hypertrophy", "Cardio HIIT + Core", "Functional + Balance"]
workouts_map = {
    "Strength + Hypertrophy": "Goblet Squat, Smith Incline Press, Lat Pulldown, Dumbbell Romanian Deadlift, Russian Twist",
    "Cardio HIIT + Core": "Jump Squat, Dumbbell Snatch (L/R), Burpee, Plank Row, Dumbbell Swing, Flutter Kicks",
    "Functional + Balance": "Bulgarian Split Squat, One-arm Shoulder Press, Smith Sumo Deadlift, Renegade Row, Single-leg Glute Bridge"
}
workout_rows = []
for week in range(1, 13):
    for day, focus in zip(weekly_schedule, focuses):
        workout_rows.append([f"Week {week}", day, focus, workouts_map[focus]])
workout_df = pd.DataFrame(workout_rows, columns=["Week","Day","Focus","Workout"])

# ---------- NEW: Load Exercise Catalog ----------
@st.cache_data
def load_catalog():
    try:
        cat = pd.read_csv("exercise_catalog.csv")
    except Exception:
        # fallback tối thiểu nếu chưa có file
        cat = pd.DataFrame(columns=["exercise","category","primary_muscle","media_url","cues","rep_low","rep_high","increment_kg"])
    # chuẩn hóa tên
    if "exercise" in cat.columns:
        cat["exercise_key"] = cat["exercise"].str.strip().str.lower()
    return cat

catalog = load_catalog()

# ---------- NEW: Local log in session (kèm download) ----------
if "log_df" not in st.session_state:
    st.session_state["log_df"] = pd.DataFrame(columns=[
        "datetime","week","day","exercise","set","weight_kg","reps","rir_or_rpe","set_time_s","notes"
    ])

def add_log_row(week, day, exercise, data_rows):
    # data_rows: list of dicts {set, weight_kg, reps, rir_or_rpe, set_time_s}
    now = datetime.now().isoformat(timespec="seconds")
    new_rows = []
    for r in data_rows:
        new_rows.append({
            "datetime": now, "week": week, "day": day, "exercise": exercise,
            "set": r.get("set",1), "weight_kg": r.get("weight_kg",0.0),
            "reps": r.get("reps",0), "rir_or_rpe": r.get("rir_or_rpe",""),
            "set_time_s": r.get("set_time_s",0), "notes": r.get("notes","")
        })
    st.session_state["log_df"] = pd.concat([st.session_state["log_df"], pd.DataFrame(new_rows)], ignore_index=True)

def history_for_exercise(ex_name):
    df = st.session_state["log_df"]
    if df.empty: return df
    return df[df["exercise"].str.lower()==ex_name.strip().lower()].sort_values("datetime")

# ---------- NEW: Auto-progression heuristic ----------
def suggest_next_load(exercise, last_weight, last_reps, rep_low, rep_high, inc):
    """
    Double progression logic (đơn giản & an toàn):
    - Nếu đạt >= rep_high: +inc kg
    - Nếu giữa rep_low và rep_high: giữ weight
    - Nếu < rep_low: -inc kg (tối thiểu về 0)
    """
    if inc is None or pd.isna(inc): inc = 2.5
    if rep_high is None or pd.isna(rep_high): rep_high = 12
    if rep_low is None or pd.isna(rep_low): rep_low = 8
    if last_weight is None or pd.isna(last_weight): last_weight = 0.0
    if last_reps is None or pd.isna(last_reps): last_reps = rep_low

    if last_reps >= rep_high:
        return max(0.0, round(last_weight + inc, 1)), f"Đạt {last_reps} ≥ {rep_high} reps → **tăng +{inc} kg**"
    elif last_reps < rep_low:
        return max(0.0, round(last_weight - inc, 1)), f"Dưới {rep_low} reps → **giảm -{inc} kg** để giữ kỹ thuật"
    else:
        return round(last_weight, 1), "Trong dải mục tiêu → **giữ mức tạ** và cố gắng tăng reps"

# ---------- TIMER đơn giản cho rest/set ----------
def rest_timer(seconds=60, key="timer"):
    if st.button(f"▶️ Bắt đầu đếm ngược {seconds}s", key=f"{key}_start"):
        st.session_state[f"{key}_start_time"] = time.time()
        st.session_state[f"{key}_duration"] = seconds
    if f"{key}_start_time" in st.session_state:
        elapsed = int(time.time() - st.session_state[f"{key}_start_time"])
        remain = max(0, st.session_state[f"{key}_duration"] - elapsed)
        st.progress(1 - remain/max(1, st.session_state[f"{key}_duration"]))
        st.write(f"⏳ Còn lại: **{remain}s**")
        if remain == 0:
            st.success("Hết thời gian nghỉ!")

# ---------- UI ----------
tab1, tab2, tab3, tab4 = st.tabs(["📅 Plan", "📝 Tracking", "📈 Gợi ý tải", "📦 Export"])

with tab1:
    st.subheader("Weekly Schedule")
    week = st.selectbox("Week", sorted(workout_df["Week"].unique(), key=lambda x:int(x.split()[-1])))
    wdf = workout_df[workout_df["Week"]==week]
    for _, row in wdf.iterrows():
        with st.expander(f"{row['Day']} — {row['Focus']}"):
            items = [x.strip() for x in row["Workout"].split(",")]
            for it in items:
                # media
                media = None
                cues = ""
                rep_low = rep_high = inc = None
                if not catalog.empty:
                    ck = it.strip().lower()
                    match = catalog[catalog["exercise_key"]==ck]
                    if not match.empty:
                        media = match["media_url"].iloc[0]
                        cues = match["cues"].iloc[0]
                        rep_low = match["rep_low"].iloc[0]
                        rep_high = match["rep_high"].iloc[0]
                        inc = match["increment_kg"].iloc[0]
                st.markdown(f"**{it}**  \n_Target reps:_ **{rep_low or 8}–{rep_high or 12}**")
                if media and isinstance(media, str) and media.startswith("http"):
                    st.image(media, use_container_width=True)
                if cues:
                    st.caption(f"Form cues: {cues}")

with tab2:
    st.subheader("Nhập set cho từng bài")
    c1, c2, c3 = st.columns(3)
    with c1:
        week = st.selectbox("Tuần", sorted(workout_df["Week"].unique(), key=lambda x:int(x.split()[-1])), key="trk_week")
    with c2:
        day = st.selectbox("Ngày", weekly_schedule, key="trk_day")
    with c3:
        # chọn exercise từ catalog trước, fallback từ plan
        ex_list = catalog["exercise"].tolist() if not catalog.empty else sorted({e for s in workouts_map.values() for e in [x.strip() for x in s.split(",")]})
        exercise = st.selectbox("Bài tập", ex_list, key="trk_ex")

    st.markdown("**Nhập dữ liệu set** (có thể sửa trong bảng):")
    default_sets = pd.DataFrame([
        {"set":1,"weight_kg":0.0,"reps":8,"rir_or_rpe":"RIR2","set_time_s":0,"notes":""},
        {"set":2,"weight_kg":0.0,"reps":8,"rir_or_rpe":"RIR2","set_time_s":0,"notes":""},
        {"set":3,"weight_kg":0.0,"reps":8,"rir_or_rpe":"RIR2","set_time_s":0,"notes":""},
    ])
    edited = st.data_editor(default_sets, num_rows="dynamic", use_container_width=True)
    rest_timer(60, key="rest1")

    if st.button("➕ Lưu các set vào lịch sử"):
        rows = edited.to_dict(orient="records")
        add_log_row(week, day, exercise, rows)
        st.success(f"Đã lưu {len(rows)} set cho {exercise}")

    if not st.session_state["log_df"].empty:
        st.markdown("### Lịch sử gần đây")
        recent = st.session_state["log_df"].tail(20)
        st.dataframe(recent, use_container_width=True)

with tab3:
    st.subheader("Gợi ý tải cho buổi kế tiếp")
    if st.session_state["log_df"].empty:
        st.info("Chưa có dữ liệu. Hãy lưu ít nhất 1 set ở tab Tracking.")
    else:
        # chọn bài để gợi ý
        ex_list_hist = sorted(st.session_state["log_df"]["exercise"].str.title().unique())
        ex_sel = st.selectbox("Chọn bài", ex_list_hist)
        hist = history_for_exercise(ex_sel)
        last = hist.sort_values(["datetime","set"]).tail(1)
        if not last.empty:
            last_weight = pd.to_numeric(last["weight_kg"]).iloc[0] if "weight_kg" in last else 0.0
            last_reps = pd.to_numeric(last["reps"]).iloc[0] if "reps" in last else 8
            # lấy target từ catalog
            rep_low = rep_high = inc = None
            if not catalog.empty:
                m = catalog[catalog["exercise_key"]==ex_sel.strip().lower()]
                if not m.empty:
                    rep_low = m["rep_low"].iloc[0]
                    rep_high = m["rep_high"].iloc[0]
                    inc = m["increment_kg"].iloc[0]
            next_load, rationale = suggest_next_load(ex_sel, last_weight, last_reps, rep_low, rep_high, inc)
            st.metric(label=f"Khuyến nghị mức tạ (kg) cho {ex_sel}", value=next_load, delta=rationale)
            st.caption("Logic: double progression (đạt đỉnh reps → tăng tải; dưới ngưỡng → giảm; còn lại → giữ).")
        else:
            st.info("Chưa có lịch sử cho bài này.")

with tab4:
    st.subheader("Export / Backup")
    st.download_button("⬇️ Tải lịch sử tập (CSV)", st.session_state["log_df"].to_csv(index=False), file_name="workout_log.csv")
    st.caption("Mẹo: tải file sau mỗi buổi để lưu backup trên iCloud/Drive.")
