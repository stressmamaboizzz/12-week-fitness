import streamlit as st
import pandas as pd
import time, os
from datetime import datetime

st.set_page_config(page_title="Tennis Performance Coach", page_icon="🎾", layout="centered")
st.title("🎾 Tennis Performance Coach")
st.caption("12-week • 3 sessions/week • 50 minutes/session — Tennis-specific strength, speed & core")

# ---------- BOOTSTRAP: auto-generate data files on first run ----------
PLAN_PATH = "tennis_plan.csv"
CAT_PATH = "exercise_catalog.csv"
ASSETS_DIR = "assets"

def ensure_bootstrap_files():
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR, exist_ok=True)
        open(os.path.join(ASSETS_DIR, ".keep"), "a").close()

    # Exercise catalog with YouTube media (plays inline)
    if not os.path.exists(CAT_PATH):
        catalog_rows = [
            # exercise, category, primary_muscle, media_url (YouTube), cues, rep_low, rep_high, increment_kg, work_sec, rest_sec
            ("Goblet Squat","Lower Body","Quads/Glutes","https://www.youtube.com/watch?v=MeIiIdhvXT4",
             "Elbows in, chest up, brace core; drive through mid-foot",8,12,2.5,0,0),
            ("Bulgarian Split Squat (Smith)","Lower Body","Quads/Glutes","https://www.youtube.com/watch?v=hiLF_pF3EJM",
             "Long stance, knee tracks toes, torso tall, full depth",8,12,2.5,0,0),
            ("Dumbbell Romanian Deadlift","Lower Body","Hamstrings/Glutes","https://www.youtube.com/watch?v=FQKfr1YDhEk",
             "Hinge hips, neutral spine, soft knees; feel hamstrings",8,12,2.5,0,0),
            ("Jump Squat","Plyometric","Quads/Glutes/Calves","https://www.youtube.com/watch?v=A-cFYWvaHr0",
             "Explode up; soft landing; absorb with hips; quality > height",0,0,0.0,30,30),
            ("Side Plank Rotation","Core","Obliques","https://www.youtube.com/watch?v=DXQ9YKHtcsk",
             "Hips high; rotate from trunk; control tempo",0,0,0.0,30,30),
            ("Ladder/Quick Feet (Cone Drill)","Agility","Ankles/Calves/Hips","https://www.youtube.com/watch?v=Kb0bfAGiub8",
             "Light/quick contacts; posture tall; eyes forward",0,0,0.0,30,30),
            ("Lunge with Twist (DB)","Core/Lower","Quads/Core","https://www.youtube.com/watch?v=7yrkGWJHSP0",
             "Step long; front knee over mid-foot; twist over lead leg",8,12,2.5,0,0),
            ("Dumbbell Slam / Speed Swing","Power","Full Body","https://www.youtube.com/watch?v=uB-fq0HqGK0",
             "Hinge then snap; arms relaxed; glutes drive the swing",0,0,0.0,20,40),
            ("Lat Pulldown","Upper Pull","Lats/Biceps","https://www.youtube.com/watch?v=SALxEARiMkw",
             "Lean ~10–20°; pull elbows to ribs; control 2–3s down",8,12,2.5,0,0),
            ("Russian Twist","Core","Obliques/Abs","https://www.youtube.com/watch?v=wkD8rjkodUI",
             "Ribs down; rotate trunk; heels light; no lumbar flexion",16,30,1.0,0,0),
            ("Push Press (DB/Smith)","Upper Push","Shoulders/Triceps","https://www.youtube.com/watch?v=MqvN10OF5fo",
             "Dip–drive vertically; brace; press to lockout with control",6,8,2.5,0,0),
            ("Dumbbell Bench Press","Upper Push","Chest/Triceps","https://www.youtube.com/watch?v=VmB1G1K7v94",
             "Scapula set; slight arch; soft lockout; full ROM",8,12,2.5,0,0),
            ("Single-arm Dumbbell Row","Upper Pull","Lats","https://www.youtube.com/watch?v=xl1YiqQY2vA",
             "Row to hip; avoid trunk rotation; squeeze at top",10,12,2.5,0,0),
            ("Shoulder External Rotation","Shoulder Care","Rotator cuff","https://www.youtube.com/watch?v=20v3G-odF5c",
             "Elbow by side; light load; slow control",12,20,1.0,0,0),
            ("Farmer Carry","Carry","Core/Grip","https://www.youtube.com/watch?v=rt17lmnaLSM",
             "Ribs down; walk tall; even steps; no sway",0,0,0.0,40,40),
        ]
        cat_df = pd.DataFrame(catalog_rows, columns=[
            "exercise","category","primary_muscle","media_url","cues",
            "rep_low","rep_high","increment_kg","work_sec","rest_sec"
        ])
        cat_df.to_csv(CAT_PATH, index=False)

    # 12-week plan with Base/Build/Peak progression (3 days/tuần)
    if not os.path.exists(PLAN_PATH):
        weeks = list(range(1,13))
        rows = []
        def phase(w): return "Base" if w<=4 else ("Build" if w<=8 else "Peak")
        for w in weeks:
            ph = phase(w)
            # --- Day A (Power/Lower)
            if ph=="Base":
                if w in [1,2]:
                    gs="4x10-12 @60-70% | Rest 75s"; bul="3x10/leg | Rest 75s"; rdl="4x8-10 | Rest 90s"
                    js="3x30s work / 30s rest"; spr="3x30-40s/side"
                else:
                    gs="4x10-12 @65-75% | Rest 75s"; bul="4x8-10/leg | Rest 75s"; rdl="4x8-10 (slow 3s down) | Rest 90s"
                    js="4x25s work / 35s rest"; spr="3x35-45s/side"
            elif ph=="Build":
                if w in [5,6,7]:
                    gs="4x8-10 @70-80% | Rest 90s"; bul="4x8-10/leg | Rest 90s"; rdl="4x8 @75-80% | Rest 90s"
                    js="4x20s work / 40s rest (max height)"; spr="3x40s/side"
                else:
                    gs="3x8-10 @65-75% | Rest 75s"; bul="3x8-10/leg | Rest 75s"; rdl="3x8 @70% | Rest 75s"
                    js="3x20s work / 40s rest"; spr="3x30-40s/side"
            else: # Peak
                if w in [9,10,11]:
                    gs="5x6-8 @75-85% (explosive concentric) | Rest 120s"; bul="4x6-8/leg (explosive up) | Rest 90s"
                    rdl="4x6-8 (pause 1s at stretch) | Rest 120s"; js="4x15-20s work / 60s rest (max quality)"
                    spr="3x45-60s/side"
                else:
                    gs="3x6-8 @70% | Rest 90s (taper)"; bul="3x8/leg | Rest 75s"; rdl="3x6-8 @70% | Rest 90s"
                    js="3x15s work / 60s rest"; spr="3x40s/side"

            rows += [
                [f"Week {w}","Day A (Power/Lower)","Goblet Squat","load",gs],
                [f"Week {w}","Day A (Power/Lower)","Bulgarian Split Squat (Smith)","load",bul],
                [f"Week {w}","Day A (Power/Lower)","Dumbbell Romanian Deadlift","load",rdl],
                [f"Week {w}","Day A (Power/Lower)","Jump Squat","time",js],
                [f"Week {w}","Day A (Power/Lower)","Side Plank Rotation","time",spr],
            ]

            # --- Day B (Agility/Core)
            if ph=="Base":
                if w in [1,2]:
                    lad="5x30s work / 30s rest (fast feet)"; ltw="3x10/side | Rest 60s"
                    slam="4x20s work / 40s rest (med ball or DB swing)"; lpd="4x10-12 | Rest 75s"; rt="3x20 | Rest 45s"
                else:
                    lad="6x30s work / 25s rest (progress speed)"; ltw="4x10/side | Rest 60s"
                    slam="5x20s work / 40s rest"; lpd="4x10-12 (2s down) | Rest 75s"; rt="3x24 | Rest 45s"
            elif ph=="Build":
                if w in [5,6,7]:
                    lad="8x20s work / 20s rest (change patterns)"; ltw="4x12/side | Rest 60s"
                    slam="6x15-20s work / 40s rest (max power)"; lpd="4x8-10 @70-80% | Rest 90s"; rt="4x20 weighted | Rest 60s"
                else:
                    lad="6x20s work / 25s rest (deload)"; ltw="3x10/side | Rest 60s"
                    slam="4x15-20s work / 45s rest"; lpd="3x10 @65-70% | Rest 75s"; rt="3x16-20 | Rest 45s"
            else:
                if w in [9,10,11]:
                    lad="10x15s work / 30s rest (max quality)"; ltw="3x8/side (controlled) | Rest 60s"
                    slam="6x10-15s work / 60s rest (max intent)"; lpd="5x6-8 @75-85% | Rest 120s"; rt="3x16-20 (slow control) | Rest 45s"
                else:
                    lad="6x15s work / 30s rest (taper)"; ltw="2x8/side | Rest 60s"
                    slam="4x10s work / 60s rest"; lpd="3x8 @70% | Rest 90s"; rt="2x16 | Rest 45s"

            rows += [
                [f"Week {w}","Day B (Agility/Core)","Ladder/Quick Feet (Cone Drill)","time",lad],
                [f"Week {w}","Day B (Agility/Core)","Lunge with Twist (DB)","load",ltw],
                [f"Week {w}","Day B (Agility/Core)","Dumbbell Slam / Speed Swing","time",slam],
                [f"Week {w}","Day B (Agility/Core)","Lat Pulldown","load",lpd],
                [f"Week {w}","Day B (Agility/Core)","Russian Twist","load",rt],
            ]

            # --- Day C (Upper/Stability)
            if ph=="Base":
                if w in [1,2]:
                    pp="4x6-8 | Rest 90s"; dbb="3x10 | Rest 75s"; row="3x12/side | Rest 60s"; ser="3x15 light | Rest 45s"; fc="3x40m walk (core braced)"
                else:
                    pp="5x6-8 | Rest 90s"; dbb="4x8-10 | Rest 75s"; row="4x10-12/side | Rest 60s"; ser="3x15-20 light | Rest 45s"; fc="4x40m walk"
            elif ph=="Build":
                if w in [5,6,7]:
                    pp="5x5-6 (explosive) | Rest 120s"; dbb="4x8-10 @70-80% | Rest 90s"; row="4x8-10/side @70-80% | Rest 90s"; ser="4x15 (slow) | Rest 45s"; fc="4x50m heavy walk"
                else:
                    pp="3x6 (deload) | Rest 90s"; dbb="3x8-10 @65-70% | Rest 75s"; row="3x10/side | Rest 75s"; ser="3x15 | Rest 45s"; fc="3x40m walk"
            else:
                if w in [9,10,11]:
                    pp="6x3-5 (speed focus) | Rest 120s"; dbb="3x6-8 (controlled) | Rest 90s"; row="3x8-10/side (strict) | Rest 90s"; ser="3x15-20 (prehab) | Rest 45s"; fc="4x60m heavy walk"
                else:
                    pp="3x3-5 (taper) | Rest 120s"; dbb="2x8 light | Rest 60s"; row="2x8/side light | Rest 60s"; ser="2x15 | Rest 45s"; fc="2x40m easy walk"

            rows += [
                [f"Week {w}","Day C (Upper/Stability)","Push Press (DB/Smith)","load",pp],
                [f"Week {w}","Day C (Upper/Stability)","Dumbbell Bench Press","load",dbb],
                [f"Week {w}","Day C (Upper/Stability)","Single-arm Dumbbell Row","load",row],
                [f"Week {w}","Day C (Upper/Stability)","Shoulder External Rotation","load",ser],
                [f"Week {w}","Day C (Upper/Stability)","Farmer Carry","time",fc],
            ]

        plan_df = pd.DataFrame(rows, columns=["Week","Day","Exercise","Type","Protocol"])
        plan_df.to_csv(PLAN_PATH, index=False)

ensure_bootstrap_files()
# ---------- END BOOTSTRAP ----------

@st.cache_data
def load_plan():
    return pd.read_csv(PLAN_PATH)

@st.cache_data
def load_catalog():
    c = pd.read_csv(CAT_PATH)
    c["exercise_key"] = c["exercise"].str.strip().str.lower()
    return c

plan_df = load_plan()
catalog = load_catalog()

if "log_df" not in st.session_state:
    st.session_state["log_df"] = pd.DataFrame(columns=["datetime","week","day","exercise","type","set","weight_kg","reps","rir_rpe","work_sec","rest_sec","notes"])

def phase_for_week(wn:int):
    if wn<=4: return "Base (capacity)"
    if wn<=8: return "Build (intensity)"
    return "Peak (power/speed)"

def show_media(media):
    if not media or str(media).strip()=="": return
    m = str(media).strip()
    if "youtube.com" in m or "youtu.be" in m: st.video(m); return
    if os.path.exists(m):
        if m.lower().endswith((".mp4",".mov",".m4v",".webm")): st.video(m)
        else: st.image(m, use_container_width=True)
    else:
        st.write(f"[Media link]({m})")

def suggest_next_load(last_weight,last_reps,rep_low,rep_high,inc):
    rep_low = rep_low if pd.notna(rep_low) and rep_low>0 else 8
    rep_high = rep_high if pd.notna(rep_high) and rep_high>0 else 12
    inc = inc if pd.notna(inc) and inc>0 else 2.5
    last_weight = last_weight if pd.notna(last_weight) else 0.0
    last_reps = last_reps if pd.notna(last_reps) else rep_low
    if last_reps>=rep_high: return round(max(0.0,last_weight+inc),1), f"Reached {last_reps} ≥ {rep_high} → **+{inc} kg**"
    if last_reps<rep_low:  return round(max(0.0,last_weight-inc),1), f"Below {rep_low} → **-{inc} kg**"
    return round(last_weight,1), "In target range → keep weight, add 1–2 reps"

def suggest_next_interval(last_work,last_rest,rpe_hint=6):
    work = int(last_work or 30); rest = int(last_rest or 30)
    if rpe_hint<=6: return work+5, max(0,rest-5), "Easy → **+5s work / -5s rest**"
    if rpe_hint>=8: return max(5,work-5), rest+5, "Hard → **-5s work / +5s rest**"
    return work, rest, "Maintain"

def add_log_rows(week,day,ex_name,ex_type,rows):
    now = datetime.now().isoformat(timespec="seconds")
    new = []
    for r in rows:
        new.append({"datetime":now,"week":week,"day":day,"exercise":ex_name,"type":ex_type,
                    "set":r.get("set",1),"weight_kg":r.get("weight_kg",0.0),"reps":r.get("reps",0),
                    "rir_rpe":r.get("rir_rpe",""),"work_sec":r.get("work_sec",0),"rest_sec":r.get("rest_sec",0),
                    "notes":r.get("notes","")})
    st.session_state["log_df"] = pd.concat([st.session_state["log_df"], pd.DataFrame(new)], ignore_index=True)

def history_for_exercise(name):
    df = st.session_state["log_df"]
    if df.empty: return df
    return df[df["exercise"].str.lower()==name.strip().lower()].sort_values(["datetime","set"])

def rest_timer(seconds=60, key="rest"):
    if st.button(f"▶️ Start {seconds}s", key=f"{key}_start"):
        st.session_state[f"{key}_start"] = time.time(); st.session_state[f"{key}_dur"]=seconds
    if f"{key}_start" in st.session_state:
        el = int(time.time()-st.session_state[f"{key}_start"]); rem = max(0, st.session_state[f"{key}_dur"]-el)
        st.progress(1 - rem/max(1, st.session_state[f"{key}_dur"])); st.write(f"⏳ {rem}s left")
        if rem==0: st.success("Done!")

tab_plan, tab_session, tab_progression, tab_media, tab_export = st.tabs(["📅 Plan","📝 Session","📈 Progression","🎬 Media","📦 Export/Import"])

with tab_plan:
    st.subheader("Weekly Schedule")
    wlist = sorted(plan_df["Week"].unique(), key=lambda x:int(str(x).split()[-1]))
    week = st.selectbox("Choose Week", wlist, index=0); phase = phase_for_week(int(str(week).split()[-1]))
    st.caption(f"Phase: **{phase}**")
    day_names = plan_df[plan_df["Week"]==week]["Day"].unique().tolist()
    day = st.selectbox("Choose Day", day_names, index=0)
    today = plan_df[(plan_df["Week"]==week)&(plan_df["Day"]==day)]
    for _, r in today.iterrows():
        ex, etype, proto = r["Exercise"], r["Type"], r["Protocol"]
        st.markdown(f"### {ex}"); st.badge(etype.upper(), variant="outline"); st.write(proto)
        media=""; cues=""; rep_low=rep_high=inc=work_sec=rest_sec=None
        m = catalog[catalog["exercise_key"]==ex.strip().lower()] if not catalog.empty else pd.DataFrame()
        if not m.empty:
            media = m["media_url"].iloc[0]; cues = m["cues"].iloc[0]; rep_low=m["rep_low"].iloc[0]; rep_high=m["rep_high"].iloc[0]
            inc=m["increment_kg"].iloc[0]; work_sec=m["work_sec"].iloc[0]; rest_sec=m["rest_sec"].iloc[0]
        show_media(media)
        if cues: st.caption(f"Cues: {cues}")
        hist = history_for_exercise(ex)
        if etype=="load":
            last = hist.tail(1); lw, lr = (last["weight_kg"].iloc[0], int(last["reps"].iloc[0])) if not last.empty else (0.0, rep_low or 8)
            nxt, why = suggest_next_load(lw, lr, rep_low, rep_high, inc); st.info(f"Next load: **{nxt} kg** — {why}")
        else:
            last = hist.tail(1); lwk = int(last["work_sec"].iloc[0]) if not last.empty else int(work_sec or 30)
            lrs = int(last["rest_sec"].iloc[0]) if not last.empty else int(rest_sec or 30)
            w2, r2, why = suggest_next_interval(lwk, lrs, 6); st.info(f"Next interval: **{w2}s / {r2}s** — {why}")
        st.markdown("---")
    if st.button("➡️ Use this day in Session"):
        st.session_state["sel_week"]=str(week); st.session_state["sel_day"]=str(day)

with tab_session:
    st.subheader("Session Tracking")
    wlist2 = sorted(plan_df["Week"].unique(), key=lambda x:int(str(x).split()[-1]))
    day_names2 = plan_df["Day"].unique().tolist()
    sel_week = st.session_state.get("sel_week", wlist2[0]); sel_day = st.session_state.get("sel_day", day_names2[0])
    st.write(f"Selected: **{sel_week} — {sel_day}**")
    today = plan_df[(plan_df["Week"]==sel_week)&(plan_df["Day"]==sel_day)]
    ex_list = today["Exercise"].tolist() if not today.empty else plan_df["Exercise"].unique().tolist()
    exercise = st.selectbox("Exercise", ex_list, index=0)
    etype = today[today["Exercise"]==exercise]["Type"].iloc[0] if not today.empty else "load"
    if etype=="load":
        st.markdown("**Enter sets (weight / reps / RIR-RPE / optional set time):**")
        default_sets = pd.DataFrame([
            {"set":1,"weight_kg":0.0,"reps":8,"rir_rpe":"RIR2","work_sec":0,"rest_sec":60,"notes":""},
            {"set":2,"weight_kg":0.0,"reps":8,"rir_rpe":"RIR2","work_sec":0,"rest_sec":60,"notes":""},
            {"set":3,"weight_kg":0.0,"reps":8,"rir_rpe":"RIR2","work_sec":0,"rest_sec":60,"notes":""},
        ])
        edited = st.data_editor(default_sets, num_rows="dynamic", use_container_width=True)
        rest_timer(60, key="rest_load")
        if st.button("➕ Save sets"):
            add_log_rows(sel_week, sel_day, exercise, "load", edited.to_dict(orient="records")); st.success(f"Saved {len(edited)} sets")
    else:
        st.markdown("**Intervals (work/rest rounds):**")
        c1,c2,c3 = st.columns(3)
        with c1: work = st.number_input("Work (s)", min_value=5, value=30, step=5)
        with c2: rest = st.number_input("Rest (s)", min_value=0, value=30, step=5)
        with c3: rounds = st.number_input("Rounds", min_value=1, value=3, step=1)
        if st.button("▶️ Start Intervals"):
            for r in range(1, rounds+1):
                st.write(f"**Round {r}/{rounds} — WORK**"); rest_timer(work, key=f"w{r}")
                st.write(f"**Round {r}/{rounds} — REST**"); rest_timer(rest, key=f"r{r}")
            st.success("Intervals finished!")
        rows = [{"set":i+1,"weight_kg":0.0,"reps":0,"rir_rpe":"","work_sec":work,"rest_sec":rest,"notes":""} for i in range(rounds)]
        if st.button("➕ Save intervals"):
            add_log_rows(sel_week, sel_day, exercise, "time", rows); st.success(f"Saved {rounds} rounds")

    if not st.session_state["log_df"].empty:
        st.markdown("### Recent log"); st.dataframe(st.session_state["log_df"].tail(30), use_container_width=True)

with tab_progression:
    st.subheader("Auto Progression")
    options = sorted(set(st.session_state["log_df"]["exercise"].tolist() + (catalog["exercise"].tolist() if not catalog.empty else [])))
    if options:
        ex_sel = st.selectbox("Exercise", options)
        hist = history_for_exercise(ex_sel)
        if hist.empty: st.info("No history yet.")
        else:
            last = hist.tail(1); etype = last["type"].iloc[0]
            if etype=="load":
                m = catalog[catalog["exercise_key"]==ex_sel.strip().lower()] if not catalog.empty else pd.DataFrame()
                rep_low = m["rep_low"].iloc[0] if not m.empty else 8; rep_high = m["rep_high"].iloc[0] if not m.empty else 12; inc = m["increment_kg"].iloc[0] if not m.empty else 2.5
                nxt, why = suggest_next_load(last["weight_kg"].iloc[0], int(last["reps"].iloc[0]), rep_low, rep_high, inc)
                st.metric(f"Next load for {ex_sel}", f"{nxt} kg"); st.caption(why)
            else:
                wsec = int(last["work_sec"].iloc[0] or 30); rsec = int(last["rest_sec"].iloc[0] or 30)
                w2, r2, why = suggest_next_interval(wsec, rsec, 6); st.metric(f"Next interval for {ex_sel}", f"{w2}s / {r2}s"); st.caption(why)
    else:
        st.info("No exercises available.")

with tab_media:
    st.subheader("Media Library")
    st.caption("YouTube links are embedded by default. You can switch to local GIF/MP4 by editing `exercise_catalog.csv` and placing files in `assets/`.")
    if catalog.empty: st.info("Upload `exercise_catalog.csv` to enable media.")
    else:
        name = st.selectbox("Exercise", catalog["exercise"].tolist())
        row = catalog[catalog["exercise"]==name].iloc[0]
        st.write(f"**{row['exercise']}** — {row['primary_muscle']}")
        show_media(row['media_url'])
        if row.get("cues"): st.caption(f"Cues: {row['cues']}")

with tab_export:
    st.subheader("Export / Import")
    st.download_button("⬇️ Download log CSV", st.session_state["log_df"].to_csv(index=False), file_name="workout_log.csv")
    up = st.file_uploader("Restore log CSV", type=["csv"])
    if up is not None:
        try:
            st.session_state["log_df"] = pd.read_csv(up); st.success("Imported log.")
        except Exception as e:
            st.error(f"Import failed: {e}")

st.markdown("---")
st.caption("Add to Home Screen on iPhone/iPad for an app-like experience. Edit `exercise_catalog.csv` to swap media (YouTube or local GIF/MP4).")
