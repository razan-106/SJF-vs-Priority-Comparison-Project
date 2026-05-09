import streamlit as st
import pandas as pd
import plotly.express as px
import copy

# ==========================================
# 1. Back-end Logic (Algorithms)
# ==========================================
def build_result(procs, gantt):
    total_wt, total_tat, total_rt = 0, 0, 0
    table = []
    for p in procs:
        tat = p['finish_time'] - p['arrival']
        wt = tat - p['burst']
        rt = p['start_time'] - p['arrival']
        total_wt, total_tat, total_rt = total_wt + wt, total_tat + tat, total_rt + rt
        table.append({'id': p['id'], 'WT': wt, 'TAT': tat, 'RT': rt})
    len_procs = len(procs) if procs else 1
    return {'gantt': gantt, 'table': table,
            'avg_wt': round(total_wt / len_procs, 2),
            'avg_tat': round(total_tat / len_procs, 2),
            'avg_rt': round(total_rt / len_procs, 2)}

def sjf_preemptive(processes):
    procs = [dict(p, remaining=p['burst'], start_time=None, finish_time=0) for p in copy.deepcopy(processes)]
    time, completed, gantt, last_process = 0, 0, [], None
    while completed < len(procs):
        available = [p for p in procs if p['arrival'] <= time and p['remaining'] > 0]
        if not available:
            time += 1; last_process = None; continue
        available.sort(key=lambda x: x['remaining'])
        current = available[0]
        if current['start_time'] is None: current['start_time'] = time
        if last_process is None or last_process['id'] != current['id']:
            gantt.append({'id': current['id'], 'start': time, 'end': time + 1})
        else: gantt[-1]['end'] += 1
        last_process = current; current['remaining'] -= 1; time += 1
        if current['remaining'] == 0:
            current['finish_time'] = time; completed += 1
    return build_result(procs, gantt)

def priority_preemptive(processes):
    procs = [dict(p, remaining=p['burst'], start_time=None, finish_time=0) for p in copy.deepcopy(processes)]
    time, completed, gantt, last_process = 0, 0, [], None
    while completed < len(procs):
        available = [p for p in procs if p['arrival'] <= time and p['remaining'] > 0]
        if not available:
            time += 1; last_process = None; continue
        available.sort(key=lambda x: (x['priority'], x['arrival']))
        current = available[0]
        if current['start_time'] is None: current['start_time'] = time
        if last_process is None or last_process['id'] != current['id']:
            gantt.append({'id': current['id'], 'start': time, 'end': time + 1})
        else: gantt[-1]['end'] += 1
        last_process = current; current['remaining'] -= 1; time += 1
        if current['remaining'] == 0:
            current['finish_time'] = time; completed += 1
    return build_result(procs, gantt)

def sjf_non_preemptive(processes):
    procs = [dict(p, start_time=None, finish_time=0, is_done=False) for p in copy.deepcopy(processes)]
    time, completed, gantt = 0, 0, []
    while completed < len(procs):
        available = [p for p in procs if p['arrival'] <= time and not p['is_done']]
        if not available:
            time += 1; continue
        available.sort(key=lambda x: (x['burst'], x['arrival']))
        current = available[0]
        current['start_time'] = time; start = time; time += current['burst']
        current['finish_time'] = time; current['is_done'] = True; completed += 1
        gantt.append({'id': current['id'], 'start': start, 'end': time})
    return build_result(procs, gantt)

def priority_non_preemptive(processes):
    procs = [dict(p, start_time=None, finish_time=0, is_done=False) for p in copy.deepcopy(processes)]
    time, completed, gantt = 0, 0, []
    while completed < len(procs):
        available = [p for p in procs if p['arrival'] <= time and not p['is_done']]
        if not available:
            time += 1; continue
        available.sort(key=lambda x: (x['priority'], x['arrival']))
        current = available[0]
        current['start_time'] = time; start = time; time += current['burst']
        current['finish_time'] = time; current['is_done'] = True; completed += 1
        gantt.append({'id': current['id'], 'start': start, 'end': time})
    return build_result(procs, gantt)

# ==========================================
# 2. Front-end UI (Streamlit)
# ==========================================

st.set_page_config(layout="wide", page_title="CPU Scheduler")

# تهيئة الذاكرة (Session State)
if 'processes' not in st.session_state: st.session_state.processes = []
if 'arr_val' not in st.session_state: st.session_state.arr_val = "0"
if 'burst_val' not in st.session_state: st.session_state.burst_val = "1"

st.title("CPU Scheduling Simulator (SJF vs Priority)")
st.markdown("*Note: Lower Priority Number = Higher Urgency (e.g., 1 is VIP)*")

# ===== زرائر السيناريوهات الجاهزة (Quick Test Buttons) =====
st.markdown("### ⚡ Quick Test Scenarios")
scen_cols = st.columns(4)

with scen_cols[0]:
    if st.button("Scenario A (Preemption Test)", use_container_width=True):
        st.session_state.processes = [
            {"Process ID": "P1", "Arrival Time": 0, "Burst Time": 5, "Priority": 3},
            {"Process ID": "P2", "Arrival Time": 1, "Burst Time": 3, "Priority": 1},
            {"Process ID": "P3", "Arrival Time": 2, "Burst Time": 8, "Priority": 2},
            {"Process ID": "P4", "Arrival Time": 3, "Burst Time": 2, "Priority": 4}
        ]
        st.rerun()

with scen_cols[1]:
    if st.button("Scenario B (Conflict Test)", use_container_width=True):
        st.session_state.processes = [
            {"Process ID": "P1", "Arrival Time": 0, "Burst Time": 2, "Priority": 4},
            {"Process ID": "P2", "Arrival Time": 1, "Burst Time": 10, "Priority": 1},
        ]
        st.rerun()

with scen_cols[2]:
    if st.button("Scenario C (Starvation Test)", use_container_width=True):
        st.session_state.processes = [
            {"Process ID": "P1", "Arrival Time": 0, "Burst Time": 8, "Priority": 10},
            {"Process ID": "P2", "Arrival Time": 1, "Burst Time": 2, "Priority": 1},
            {"Process ID": "P3", "Arrival Time": 2, "Burst Time": 2, "Priority": 2},
            {"Process ID": "P4", "Arrival Time": 3, "Burst Time": 2, "Priority": 1},
            {"Process ID": "P5", "Arrival Time": 4, "Burst Time": 1, "Priority": 2}
        ]
        st.rerun()

with scen_cols[3]:
    if st.button("Scenario D (Validation Demo)", use_container_width=True):
        st.session_state.processes = [] # مسح الجدول
        st.session_state.arr_val = "-1"  # وضع قيمة غلط
        st.session_state.burst_val = "0" # وضع قيمة غلط
        st.rerun()

st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. Input Process")
    p_id = st.text_input("Process ID (e.g., P1)", key="p_id_input")
    arrival_time_str = st.text_input("Arrival Time", value=st.session_state.arr_val)
    burst_time_str = st.text_input("Burst Time", value=st.session_state.burst_val)
    priority_str = st.text_input("Priority", "1")
    
    if st.button("Add Process", use_container_width=True, type="primary"):
        error = False
        try:
            arr_time, burst_time, priority = int(arrival_time_str), int(burst_time_str), int(priority_str)
            existing_ids = [p["Process ID"] for p in st.session_state.processes]
            if not p_id.strip(): st.error("Process ID cannot be empty"); error = True
            elif p_id in existing_ids: st.error("Process ID already exists"); error = True
            elif arr_time < 0: st.error("Arrival Time cannot be negative"); error = True
            elif burst_time <= 0: st.error("Burst Time must be greater than zero"); error = True
            elif priority <= 0: st.error("Priority must be greater than zero"); error = True
            if not error:
                st.session_state.processes.append({"Process ID": p_id, "Arrival Time": arr_time, "Burst Time": burst_time, "Priority": priority})
                st.success(f"'{p_id}' Added Successfully!")
                st.session_state.arr_val = "0" # إعادة القيم للوضع الطبيعي
                st.session_state.burst_val = "1"
        except ValueError:
            st.error("Please enter valid integer values.")

    if st.button("Clear All Table", type="secondary", use_container_width=True):
        st.session_state.processes = []
        st.session_state.arr_val = "0"
        st.session_state.burst_val = "1"
        st.rerun()

with col2:
    st.header("2. Processes Table")
    if len(st.session_state.processes) > 0:
        df_input = pd.DataFrame(st.session_state.processes)
        st.dataframe(df_input, use_container_width=True)
        st.divider()
        if st.button("COMPARE ALL ALGORITHMS", type="primary", use_container_width=True):
            logic_input = [{'id': p['Process ID'], 'arrival': p['Arrival Time'], 'burst': p['Burst Time'], 'priority': p['Priority']} for p in st.session_state.processes]
            sjf_pre, prio_pre, sjf_non, prio_non = sjf_preemptive(logic_input), priority_preemptive(logic_input), sjf_non_preemptive(logic_input), priority_non_preemptive(logic_input)
            
            def display_results(title, res):
                st.subheader(title)
                g_list = [{'Task': g['id'], 'Start': g['start'], 'Duration': g['end'] - g['start']} for g in res['gantt']]
                if g_list:
                    fig = px.bar(pd.DataFrame(g_list), base="Start", x="Duration", y="Task", color="Task", orientation='h', height=250)
                    fig.update_layout(xaxis_title="Time", yaxis_title="Processes", showlegend=False, margin=dict(t=10, b=10))
                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{title}")
                t_list = [{'Process ID': t['id'], 'RT': t['RT'], 'WT': t['WT'], 'TAT': t['TAT']} for t in res['table']]
                st.dataframe(pd.DataFrame(t_list), use_container_width=True)
                st.info(f"**Averages:** WT = {res['avg_wt']} ms | TAT = {res['avg_tat']} ms | RT = {res['avg_rt']} ms")

            st.success("Simulation Complete! Scroll down for Summary.")
            display_results("1. Shortest Job First (SJF) - Preemptive", sjf_pre)
            display_results("2. Priority Scheduling - Preemptive", prio_pre)
            st.divider()
            display_results("3. Shortest Job First (SJF) - Non-Preemptive", sjf_non)
            display_results("4. Priority Scheduling - Non-Preemptive", prio_non)

            st.divider()
            st.markdown("### 📊 Comparison Summary & Final Conclusion")
            summary_df = pd.DataFrame({
                'Algorithm': ['SJF (Preemptive)', 'Priority (Preemptive)', 'SJF (Non-Preemptive)', 'Priority (Non-Preemptive)'],
                'Avg Waiting Time': [sjf_pre['avg_wt'], prio_pre['avg_wt'], sjf_non['avg_wt'], prio_non['avg_wt']],
                'Avg Turnaround': [sjf_pre['avg_tat'], prio_pre['avg_tat'], sjf_non['avg_tat'], prio_non['avg_tat']]
            })
            st.table(summary_df.set_index('Algorithm'))
            
            st.subheader("Final Conclusion")
            st.markdown("""
            - **SJF Preemptive** is the most efficient, achieving the lowest average waiting times.
            - **Priority Scheduling** focuses on urgency but can cause **Starvation** for low-priority tasks (as seen in Scenario C).
            - There is a clear **Trade-off** between total system efficiency and the ability to handle urgent tasks immediately.
            """)
    else:
        st.info("No processes added. Use quick scenarios above or add manually.")