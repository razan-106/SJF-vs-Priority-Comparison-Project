let processes = [];
const colors = ['#3498db', '#e74c3c', '#2ecc71', '#f1c40f', '#9b59b6'];

// --- Helper Functions ---
function deepCopy(data) { return JSON.parse(JSON.stringify(data)); }

function buildResult(procs, gantt) {
    let total_wt = 0, total_tat = 0, total_rt = 0;
    const table = procs.map(p => {
        const tat = p.finish_time - p.arrival;
        const wt = tat - p.burst;
        const rt = p.start_time - p.arrival;
        total_wt += wt; total_tat += tat; total_rt += rt;
        return { id: p.id, WT: wt, TAT: tat, RT: rt };
    });
    return { gantt, table, avg_wt: (total_wt/procs.length).toFixed(2), avg_tat: (total_tat/procs.length).toFixed(2), avg_rt: (total_rt/procs.length).toFixed(2) };
}

// --- Algorithms ---
function sjf_preemptive(input) {
    let procs = deepCopy(input).map(p => ({...p, remaining: p.burst, start_time: null, finish_time: 0}));
    let time = 0, completed = 0, gantt = [], last_id = null;
    while (completed < procs.length) {
        let available = procs.filter(p => p.arrival <= time && p.remaining > 0).sort((a,b) => a.remaining - b.remaining);
        if (available.length === 0) { time++; last_id = null; continue; }
        let curr = available[0];
        if (curr.start_time === null) curr.start_time = time;
        if (last_id !== curr.id) gantt.push({id: curr.id, start: time, end: time + 1});
        else gantt[gantt.length-1].end++;
        last_id = curr.id; curr.remaining--; time++;
        if (curr.remaining === 0) { curr.finish_time = time; completed++; }
    }
    return buildResult(procs, gantt);
}

function priority_preemptive(input) {
    let procs = deepCopy(input).map(p => ({...p, remaining: p.burst, start_time: null, finish_time: 0}));
    let time = 0, completed = 0, gantt = [], last_id = null;
    while (completed < procs.length) {
        let available = procs.filter(p => p.arrival <= time && p.remaining > 0).sort((a,b) => a.priority - b.priority || a.arrival - b.arrival);
        if (available.length === 0) { time++; last_id = null; continue; }
        let curr = available[0];
        if (curr.start_time === null) curr.start_time = time;
        if (last_id !== curr.id) gantt.push({id: curr.id, start: time, end: time + 1});
        else gantt[gantt.length-1].end++;
        last_id = curr.id; curr.remaining--; time++;
        if (curr.remaining === 0) { curr.finish_time = time; completed++; }
    }
    return buildResult(procs, gantt);
}

function sjf_non_preemptive(input) {
    let procs = deepCopy(input).map(p => ({...p, start_time: null, is_done: false}));
    let time = 0, completed = 0, gantt = [];
    while (completed < procs.length) {
        let available = procs.filter(p => p.arrival <= time && !p.is_done).sort((a,b) => a.burst - b.burst || a.arrival - b.arrival);
        if (available.length === 0) { time++; continue; }
        let curr = available[0];
        curr.start_time = time; let start = time; time += curr.burst;
        curr.finish_time = time; curr.is_done = true; completed++;
        gantt.push({id: curr.id, start, end: time});
    }
    return buildResult(procs, gantt);
}

function priority_non_preemptive(input) {
    let procs = deepCopy(input).map(p => ({...p, start_time: null, is_done: false}));
    let time = 0, completed = 0, gantt = [];
    while (completed < procs.length) {
        let available = procs.filter(p => p.arrival <= time && !p.is_done).sort((a,b) => a.priority - b.priority || a.arrival - b.arrival);
        if (available.length === 0) { time++; continue; }
        let curr = available[0];
        curr.start_time = time; let start = time; time += curr.burst;
        curr.finish_time = time; curr.is_done = true; completed++;
        gantt.push({id: curr.id, start, end: time});
    }
    return buildResult(procs, gantt);
}

// --- UI Logic ---
function loadScenario(type) {
    processes = [];
    if (type === 'A') {
        processes = [{id:'P1', arrival:0, burst:5, priority:3}, {id:'P2', arrival:1, burst:3, priority:1}, {id:'P3', arrival:2, burst:8, priority:2}, {id:'P4', arrival:3, burst:2, priority:4}];
    } else if (type === 'B') {
        processes = [{id:'P1', arrival:0, burst:2, priority:4}, {id:'P2', arrival:1, burst:10, priority:1}];
    } else if (type === 'C') {
        processes = [{id:'P1', arrival:0, burst:8, priority:10}, {id:'P2', arrival:1, burst:2, priority:1}, {id:'P3', arrival:2, burst:2, priority:2}, {id:'P4', arrival:3, burst:2, priority:1}, {id:'P5', arrival:4, burst:1, priority:2}];
    } else if (type === 'D') {
        document.getElementById('arr_time').value = "-1";
        document.getElementById('burst_time').value = "0";
        alert("Scenario D: Invalid inputs set. Click 'Add Process' to see validation.");
        renderTable(); return;
    }
    renderTable();
}

function renderTable() {
    const body = document.getElementById('process-table-body');
    const placeholder = document.getElementById('table-placeholder');
    body.innerHTML = '';
    processes.length > 0 ? placeholder.classList.add('hidden') : placeholder.classList.remove('hidden');
    processes.forEach(p => {
        body.innerHTML += `<tr><td>${p.id}</td><td>${p.arrival}</td><td>${p.burst}</td><td>${p.priority}</td></tr>`;
    });
}

document.getElementById('process-form').onsubmit = (e) => {
    e.preventDefault();
    const id = document.getElementById('p_id').value.trim();
    const arr = parseInt(document.getElementById('arr_time').value);
    const burst = parseInt(document.getElementById('burst_time').value);
    const prio = parseInt(document.getElementById('priority').value);

    if (!id) { alert("Process ID required"); return; }
    if (processes.some(p => p.id === id)) { alert("ID exists"); return; }
    if (isNaN(arr) || arr < 0) { alert("Arrival Time cannot be negative"); return; }
    if (isNaN(burst) || burst <= 0) { alert("Burst Time must be > 0"); return; }
    if (isNaN(prio) || prio <= 0) { alert("Priority must be > 0"); return; }

    processes.push({id, arrival:arr, burst, priority:prio});
    renderTable();
};

document.getElementById('clear-btn').onclick = () => { processes = []; renderTable(); document.getElementById('results-container').classList.add('hidden'); };

function renderResults(title, res, container) {
    const totalTime = Math.max(...res.gantt.map(g => g.end));
    let html = `<div class="result-section"><h3>${title}</h3><div class="gantt-container">`;
    const uniqueIds = [...new Set(res.gantt.map(g => g.id))];
    uniqueIds.forEach(id => {
        html += `<div class="gantt-row"><div class="gantt-label">${id}</div><div class="gantt-chart">`;
        res.gantt.filter(g => g.id === id).forEach(seg => {
            const left = (seg.start / totalTime) * 100;
            const width = ((seg.end - seg.start) / totalTime) * 100;
            const color = colors[processes.findIndex(p => p.id === id) % colors.length];
            html += `<div class="gantt-bar" style="left:${left}%; width:${width}%; background:${color}">${seg.start}-${seg.end}</div>`;
        });
        html += `</div></div>`;
    });
    html += `</div><table><thead><tr><th>ID</th><th>RT</th><th>WT</th><th>TAT</th></tr></thead><tbody>`;
    res.table.forEach(r => html += `<tr><td>${r.id}</td><td>${r.RT}</td><td>${r.WT}</td><td>${r.TAT}</td></tr>`);
    html += `</tbody></table><div class="averages">Averages: WT=${res.avg_wt} | TAT=${res.avg_tat} | RT=${res.avg_rt}</div></div>`;
    container.innerHTML += html;
}

document.getElementById('compare-btn').onclick = () => {
    if (processes.length === 0) return alert("Add processes first");
    const container = document.getElementById('results-container');
    container.innerHTML = '<h2>Simulation Results</h2>';
    container.classList.remove('hidden');

    const s_pre = sjf_preemptive(processes), p_pre = priority_preemptive(processes);
    const s_non = sjf_non_preemptive(processes), p_non = priority_non_preemptive(processes);

    container.innerHTML += '<h3>🔴 Part 1: Preemptive</h3>';
    renderResults("1. SJF - Preemptive", s_pre, container);
    renderResults("2. Priority - Preemptive", p_pre, container);
    container.innerHTML += '<hr><h3>🔵 Part 2: Non-Preemptive</h3>';
    renderResults("3. SJF - Non-Preemptive", s_non, container);
    renderResults("4. Priority - Non-Preemptive", p_non, container);

    container.innerHTML += `
        <hr><h3>📊 Comparison Summary & Final Conclusion</h3>
        <table class="summary-table">
            <thead><tr><th>Algorithm</th><th>Avg WT</th><th>Avg TAT</th></tr></thead>
            <tbody>
                <tr><td>SJF (Pre)</td><td>${s_pre.avg_wt}</td><td>${s_pre.avg_tat}</td></tr>
                <tr><td>Priority (Pre)</td><td>${p_pre.avg_wt}</td><td>${p_pre.avg_tat}</td></tr>
                <tr><td>SJF (Non)</td><td>${s_non.avg_wt}</td><td>${s_non.avg_tat}</td></tr>
                <tr><td>Priority (Non)</td><td>${p_non.avg_wt}</td><td>${p_non.avg_tat}</td></tr>
            </tbody>
        </table>
        <div class="conclusion-box">
            <p><b>Final Conclusion:</b> <br> <b>SJF Preemptive</b> is the most efficient, achieving the lowest average waiting times.<br>
            <b>Priority Scheduling</b> focuses on urgency but can cause <b>Starvation</b> for low-priority tasks (as seen in Scenario C).<br>
            There is a clear <b>Trade-off</b> between total system efficiency and the ability to handle urgent tasks immediately.</p>
        </div>`;
};