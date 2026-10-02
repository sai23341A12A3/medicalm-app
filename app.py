import streamlit as st
import datetime
import re

# Page Configuration
st.set_page_config(
    page_title="MediCalm — AI Medical Assistant & Medicine Reminder",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Medical Theme Styling (Emerald / Teal / Calm Slate)
st.markdown("""
<style>
    :root {
        --primary: #0d9488;
        --primary-light: #14b8a6;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0f766e;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .subtitle {
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .reminder-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 6px solid #0d9488;
        border-radius: 12px;
        padding: 1.1rem 1.4rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .reminder-card.taken {
        border-left-color: #10b981;
        background: #f0fdf4;
        opacity: 0.85;
    }
    .reminder-time {
        font-size: 1.3rem;
        font-weight: 800;
        color: #0f172a;
    }
    .reminder-name {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f766e;
    }
    .badge-taken {
        background: #dcfce7;
        color: #15803d;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 700;
    }
    .badge-pending {
        background: #e0f2fe;
        color: #0369a1;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 700;
    }
    .emergency-box {
        background: #fff1f2;
        border: 1.5px solid #fecdd3;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        color: #be123c;
        margin-bottom: 1rem;
    }
    .stat-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions for schedule parsing
def format_time_12h(time_24):
    try:
        t = datetime.datetime.strptime(time_24.strip(), "%H:%M")
        return t.strftime("%I:%M %p").lstrip('0')
    except Exception:
        return time_24

def parse_schedule_input(text):
    lines = [l.strip() for l in re.split(r'[\n,;]+', text) if l.strip()]
    items = []
    for line in lines:
        time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)', line, re.IGNORECASE)
        time_str = "8:00 AM"
        if time_match:
            time_str = time_match.group(1).upper()
            if ":" not in time_str:
                time_str = re.sub(r'(\d+)\s*(AM|PM)', r'\1:00 \2', time_str)

        clean = re.sub(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)', '', line, flags=re.IGNORECASE)
        clean = re.sub(r'[→\->:]+', '', clean).replace('at', '').replace('take', '').strip()

        # dosage
        dose_match = re.search(r'(\d+(?:\.\d+)?\s*(?:mg|ml|tablet|capsule|puff)s?)', clean, re.IGNORECASE)
        dosage = dose_match.group(1) if dose_match else "1 dose"
        if dose_match:
            clean = clean.replace(dose_match.group(0), '').strip()

        med_name = clean.strip() or "Medicine"
        items.append({
            "id": f"rem_{len(items)}_{med_name}",
            "time": time_str,
            "name": med_name,
            "dosage": dosage,
            "instructions": "After meal" if "after" in line.lower() else "With water",
            "taken": False
        })
    return items

# Initialize Session State
if "reminders" not in st.session_state:
    st.session_state.reminders = [
        {"id": "1", "time": "8:00 AM", "name": "Medicine A", "dosage": "500 mg", "instructions": "After breakfast", "taken": False},
        {"id": "2", "time": "2:00 PM", "name": "Medicine B", "dosage": "250 mg", "instructions": "After lunch", "taken": False},
        {"id": "3", "time": "9:00 PM", "name": "Medicine A", "dosage": "500 mg", "instructions": "After dinner", "taken": False},
    ]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hello! I am MediCalm's Clinical Companion. Describe any symptoms you have or ask about medications."}
    ]

# Sidebar Navigation
with st.sidebar:
    st.markdown("## 🩺 MediCalm")
    st.markdown("**AI Health Assistant & Scheduler**")
    st.markdown("---")
    menu = st.radio(
        "Navigation",
        [
            "⏰ Medicine Reminder",
            "🩺 Symptom Checker",
            "💊 Medicine Info",
            "📋 Lab Report Analyzer",
            "📖 Health Education",
            "📊 Compliance & History"
        ],
        index=0
    )
    st.markdown("---")
    st.caption("Educational guidance only — not a substitute for professional medical care.")

# -------------------------------------------------------------
# TAB 1: MEDICINE REMINDER
# -------------------------------------------------------------
if menu == "⏰ Medicine Reminder":
    st.markdown('<div class="main-title">⏰ Medicine Reminder & Daily Schedule</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Enter your schedule to generate structured daily reminders with adherence tracking.</div>', unsafe_allow_html=True)

    # Adherence metrics
    total = len(st.session_state.reminders)
    taken = sum(1 for r in st.session_state.reminders if r["taken"])
    pct = int((taken / total) * 100) if total > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Today's Adherence", value=f"{pct}%")
        st.progress(pct / 100)
    with col2:
        st.metric(label="Completed Doses", value=f"{taken} of {total}")
    with col3:
        st.metric(label="Adherence Streak", value="4 Days 🔥")

    st.markdown("---")

    # Smart Input Generator
    st.markdown("### ⚡ Quick Schedule Generator")
    st.write("Type or paste your schedule in plain text (e.g. `8:00 AM → Medicine A`):")

    preset_cols = st.columns([1, 1, 1, 3])
    with preset_cols[0]:
        if st.button("⭐ Load Sample (A & B)"):
            st.session_state.schedule_text = "8:00 AM → Medicine A\n2:00 PM → Medicine B\n9:00 PM → Medicine A"
    with preset_cols[1]:
        if st.button("💊 Antibiotic (3x Day)"):
            st.session_state.schedule_text = "8:00 AM → Amoxicillin 500mg\n2:00 PM → Amoxicillin 500mg\n9:00 PM → Amoxicillin 500mg"
    with preset_cols[2]:
        if st.button("🩺 BP & Diabetes Care"):
            st.session_state.schedule_text = "8:00 AM → Amlodipine 5mg\n8:00 AM → Metformin 500mg\n8:00 PM → Metformin 500mg"

    default_text = getattr(st.session_state, "schedule_text", "8:00 AM → Medicine A\n2:00 PM → Medicine B\n9:00 PM → Medicine A")
    user_input = st.text_area("Medication Schedule Input", value=default_text, height=100)

    if st.button("✨ Generate Daily Reminders", type="primary"):
        parsed = parse_schedule_input(user_input)
        if parsed:
            st.session_state.reminders = parsed
            st.success("Daily reminders generated successfully!")
            st.rerun()

    st.markdown("---")

    # Generated Schedule Timeline View
    st.markdown("### 📋 Today's Generated Reminders")

    if not st.session_state.reminders:
        st.info("No reminders scheduled. Use the generator above to create your schedule.")
    else:
        for idx, item in enumerate(st.session_state.reminders):
            card_col1, card_col2, card_col3 = st.columns([2, 4, 2])
            with card_col1:
                st.markdown(f"### **{item['time']}**")
            with card_col2:
                status_badge = "✅ TAKEN" if item['taken'] else "⏳ PENDING"
                st.markdown(f"**→ {item['name']}** ({item['dosage']})  `{status_badge}`")
                st.caption(f"Instructions: {item['instructions']}")
            with card_col3:
                btn_label = "Undo" if item['taken'] else "Mark Taken"
                if st.button(btn_label, key=f"btn_{item['id']}_{idx}"):
                    item['taken'] = not item['taken']
                    if all(r['taken'] for r in st.session_state.reminders):
                        st.balloons()
                        st.toast("🎉 Awesome! All doses for today completed!")
                    st.rerun()
            st.divider()

    # Manual Add Form (Expander)
    with st.expander("➕ Add Single Medicine Manually"):
        with st.form("manual_add_form"):
            m_name = st.text_input("Medicine Name", placeholder="e.g. Paracetamol, Metformin")
            m_dose = st.text_input("Dosage", placeholder="e.g. 500 mg, 1 tablet")
            m_time = st.time_input("Scheduled Time", value=datetime.time(8, 0))
            m_food = st.selectbox("Timing relation", ["After meal", "Before meal", "With food", "At bedtime", "With water"])
            submitted = st.form_submit_button("Add to Schedule")
            if submitted and m_name:
                formatted_t = m_time.strftime("%I:%M %p").lstrip("0")
                st.session_state.reminders.append({
                    "id": f"rem_manual_{len(st.session_state.reminders)}",
                    "time": formatted_t,
                    "name": m_name,
                    "dosage": m_dose or "1 dose",
                    "instructions": m_food,
                    "taken": False
                })
                st.success(f"Added {m_name} at {formatted_t}")
                st.rerun()

    # Download Schedule
    sched_summary = "MEDICINE SCHEDULE REMINDERS\n" + "="*30 + "\n"
    for r in st.session_state.reminders:
        status_txt = "Completed" if r['taken'] else "Pending"
        sched_summary += f"{r['time']} -> {r['name']} ({r['dosage']}) - {r['instructions']} [{status_txt}]\n"

    st.download_button("📥 Export Schedule (.txt)", data=sched_summary, file_name="medicine_schedule.txt")

# -------------------------------------------------------------
# TAB 2: SYMPTOM CHECKER
# -------------------------------------------------------------
elif menu == "🩺 Symptom Checker":
    st.markdown('<div class="main-title">🩺 Symptom Checker</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Describe your symptoms to receive patient-friendly possibilities and emergency checks.</div>', unsafe_allow_html=True)

    # Red Flag Warning
    st.markdown("""
    <div class="emergency-box">
        <strong>⚠️ Built-in Emergency Detection:</strong> If you experience crushing chest pain, difficulty breathing, sudden face droop, severe bleeding, or loss of consciousness, seek immediate emergency medical care.
    </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_query = st.chat_input("Describe your symptoms (e.g. headache, fever, cough)...")
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Emergency check
        is_emergency = bool(re.search(r'chest\s*pain|cannot\s*breathe|shortness\s*of\s*breath|stroke|severe\s*bleeding|unconscious', user_query, re.I))

        if is_emergency:
            bot_reply = "🚨 **EMERGENCY WARNING DETECTED**\n\nThe symptoms you described may indicate a critical medical emergency. **Do not delay.** Call your local emergency medical services (911 / 112) immediately."
        elif re.search(r'headache|migraine', user_query, re.I):
            bot_reply = "### Headache Assessment\n- **Tension Headache:** Common; tight band feeling around head. Often linked to stress, screen fatigue, or dehydration.\n- **Migraine:** Throbbing, usually one-sided, sometimes with light sensitivity.\n- **Support:** Drink water, rest in a quiet dark room, apply cool forehead compress."
        elif re.search(r'fever|chills', user_query, re.I):
            bot_reply = "### Fever Guidance\n- **Immune Response:** Fever helps the body fight infection.\n- **Self-care:** Stay well hydrated, rest, and monitor temperature.\n- **Doctor visit:** Consult if fever exceeds 103°F (39.4°C) or lasts over 3 days."
        elif re.search(r'cough|cold|throat', user_query, re.I):
            bot_reply = "### Cough & Cold Support\n- Most mild coughs and colds are viral and resolve within 5–7 days.\n- Warm salt water gargles and honey with warm water provide natural throat soothing."
        else:
            bot_reply = "Thank you for sharing your symptoms. Ensure adequate rest and fluid intake. If symptoms persist for more than 48 hours or worsen, consult a qualified healthcare provider."

        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)

# -------------------------------------------------------------
# TAB 3: MEDICINE INFO
# -------------------------------------------------------------
elif menu == "💊 Medicine Info":
    st.markdown('<div class="main-title">💊 Medicine Directory</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Search common medicines for uses, standard dosages, precautions, and meal timing.</div>', unsafe_allow_html=True)

    meds = [
        {"name": "Paracetamol (Acetaminophen)", "dosage": "500 mg - 650 mg every 4-6 hrs", "uses": "Pain relief & fever reduction", "timing": "With or without food", "precautions": "Max 4,000 mg/day. Caution in liver disease."},
        {"name": "Ibuprofen", "dosage": "200 mg - 400 mg every 4-6 hrs", "uses": "Inflammation, dental pain, body aches", "timing": "Always after food", "precautions": "Avoid in active stomach ulcers or severe renal issues."},
        {"name": "Amoxicillin", "dosage": "250 mg - 500 mg every 8 hrs", "uses": "Bacterial respiratory & ear/throat infections", "timing": "After meal", "precautions": "Complete full prescribed course. Penicillin allergy alert."},
        {"name": "Metformin", "dosage": "500 mg twice daily with meals", "uses": "Type 2 Diabetes glucose control", "timing": "With breakfast & dinner", "precautions": "Take with meals to prevent gastrointestinal upset."},
        {"name": "Atorvastatin", "dosage": "10 mg - 40 mg once daily", "uses": "Cholesterol lowering & cardiovascular health", "timing": "At bedtime", "precautions": "Avoid grapefruit. Report unexplained muscle pain."},
        {"name": "Omeprazole", "dosage": "20 mg - 40 mg once daily", "uses": "Acid reflux, GERD, and heartburn", "timing": "30-60 mins before breakfast", "precautions": "Best taken on empty stomach."}
    ]

    search = st.text_input("🔍 Search medicine by name...", placeholder="e.g. Paracetamol, Metformin, Ibuprofen")
    filtered = [m for m in meds if search.lower() in m["name"].lower() or search.lower() in m["uses"].lower()]

    for m in filtered:
        with st.expander(f"💊 {m['name']} — {m['uses']}"):
            st.write(f"**Typical Dosage:** {m['dosage']}")
            st.write(f"**Meal Timing:** {m['timing']}")
            st.write(f"**Precautions:** {m['precautions']}")
            if st.button(f"Add {m['name'].split()[0]} to Reminder Schedule", key=f"add_{m['name']}"):
                st.session_state.reminders.append({
                    "id": f"rem_{len(st.session_state.reminders)}",
                    "time": "08:00 AM",
                    "name": m['name'].split()[0],
                    "dosage": m['dosage'].split()[0] + " " + m['dosage'].split()[1] if len(m['dosage'].split()) > 1 else "1 dose",
                    "instructions": m['timing'],
                    "taken": False
                })
                st.success(f"Added {m['name'].split()[0]} to your schedule!")

# -------------------------------------------------------------
# TAB 4: LAB REPORT ANALYZER
# -------------------------------------------------------------
elif menu == "📋 Lab Report Analyzer":
    st.markdown('<div class="main-title">📋 Lab Report Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Enter blood test values for plain-English evaluations against standard reference intervals.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        hb = st.number_input("Hemoglobin (Hb) [g/dL]", min_value=1.0, max_value=25.0, value=14.2, step=0.1)
        fbs = st.number_input("Fasting Blood Sugar [mg/dL]", min_value=30.0, max_value=500.0, value=92.0, step=1.0)
        hba1c = st.number_input("HbA1c [%]", min_value=3.0, max_value=18.0, value=5.4, step=0.1)
    with col2:
        chol = st.number_input("Total Cholesterol [mg/dL]", min_value=50.0, max_value=600.0, value=185.0, step=1.0)
        creat = st.number_input("Serum Creatinine [mg/dL]", min_value=0.2, max_value=15.0, value=0.9, step=0.05)

    st.markdown("### 📊 Assessment Summary")
    hb_status = "Normal" if 12.0 <= hb <= 16.5 else ("Low (Anemia risk)" if hb < 12.0 else "High")
    fbs_status = "Normal" if 70 <= fbs <= 99 else ("Prediabetes" if 100 <= fbs <= 125 else "Elevated (Diabetes range)")
    hba1c_status = "Normal" if hba1c < 5.7 else ("Prediabetes" if 5.7 <= hba1c <= 6.4 else "Diabetic range (≥6.5%)")

    st.write(f"- **Hemoglobin ({hb} g/dL):** `{hb_status}` (Reference: 12.0 – 16.5 g/dL)")
    st.write(f"- **Fasting Glucose ({fbs} mg/dL):** `{fbs_status}` (Reference: 70 – 99 mg/dL)")
    st.write(f"- **HbA1c ({hba1c}%):** `{hba1c_status}` (Reference: < 5.7%)")
    st.write(f"- **Total Cholesterol ({chol} mg/dL):** `{'Normal (<200)' if chol <= 200 else 'Elevated (>200)'}`")
    st.write(f"- **Creatinine ({creat} mg/dL):** `{'Normal (0.6 - 1.2)' if 0.6 <= creat <= 1.2 else 'Outside reference range'}`")

# -------------------------------------------------------------
# TAB 5: HEALTH EDUCATION
# -------------------------------------------------------------
elif menu == "📖 Health Education":
    st.markdown('<div class="main-title">📖 Health Education</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Plain-language clinical guides on chronic wellness and first aid.</div>', unsafe_allow_html=True)

    with st.expander("❤️ Blood Pressure Numbers & DASH Diet"):
        st.write("""
        - **Normal:** < 120 / < 80 mmHg
        - **Elevated:** 120-129 / < 80 mmHg
        - **Stage 1 Hypertension:** 130-139 / 80-89 mmHg
        - **Tip:** Reduce dietary sodium to under 1,500 mg/day, engage in 30 minutes of aerobic exercise, and never skip prescribed antihypertensives.
        """)

    with st.expander("🩸 Diabetes Essentials & Hypoglycemia (Rule of 15)"):
        st.write("""
        - **Fasting Target:** 70–99 mg/dL
        - **Postprandial (2 hrs after meal):** < 140 mg/dL
        - **Rule of 15 for Low Sugar (<70 mg/dL):** Consume 15g fast-acting sugar (1/2 cup fruit juice), wait 15 minutes, and re-test.
        """)

    with st.expander("🛡️ First Aid: Burns & Choking"):
        st.write("""
        - **Minor Burns:** Cool under running tap water for 10–15 minutes. Never use ice or butter. Cover with clean dressing.
        - **Choking:** Deliver 5 back blows followed by 5 abdominal thrusts (Heimlich maneuver).
        """)

# -------------------------------------------------------------
# TAB 6: COMPLIANCE & HISTORY
# -------------------------------------------------------------
elif menu == "📊 Compliance & History":
    st.markdown('<div class="main-title">📊 Health History & Adherence</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Review your daily medication compliance records.</div>', unsafe_allow_html=True)

    total = len(st.session_state.reminders)
    taken = sum(1 for r in st.session_state.reminders if r["taken"])
    pct = int((taken / total) * 100) if total > 0 else 0

    st.markdown(f"### Overall Today's Adherence: **{pct}%**")
    st.progress(pct / 100)

    st.markdown("### Log of Doses")
    for r in st.session_state.reminders:
        status_icon = "🟢 Completed" if r['taken'] else "⚪ Pending"
        st.write(f"{status_icon} — **{r['time']}**: {r['name']} ({r['dosage']})")
