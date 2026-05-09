# 📊 Project Test Scenarios

This document details the test cases used to validate the accuracy and robustness of the CPU Scheduling Simulator. 

---

### 🟢 Scenario A: Basic Preemption & Logic Test
**Objective:** To verify that the simulator handles basic preemption and calculates metrics correctly for a standard workload.

| Process ID | Arrival Time | Burst Time | Priority (1=VIP) |
| :--- | :--- | :--- | :--- |
| P1 | 0 | 5 | 3 |
| P2 | 1 | 3 | 1 |
| P3 | 2 | 8 | 2 |
| P4 | 3 | 2 | 4 |

**Expected Behavior:** 
- In **SJF Preemptive**, P1 should be preempted by P2 because P2 has a shorter remaining time.
- In **Priority Preemptive**, P1 should be preempted by P2 because P2 has a higher priority (1).

---

### 🟡 Scenario B: Conflict between Burst Time and Priority
**Objective:** To reveal the core difference between the two algorithms.

| Process ID | Arrival Time | Burst Time | Priority (1=VIP) |
| :--- | :--- | :--- | :--- |
| P1 | 0 | 2 | 4 |
| P2 | 1 | 10 | 1 |

**Expected Behavior:**
- **SJF** will favor P1 due to its short burst time.
- **Priority** will favor P2 (even though it's much longer) because it is a VIP process.
- This demonstrates the **Trade-off** between efficiency (SJF) and urgency (Priority).

---

### 🔴 Scenario C: Fairness & Starvation Case
**Objective:** To observe the "Starvation" phenomenon where a process is delayed indefinitely.

| Process ID | Arrival Time | Burst Time | Priority (1=VIP) |
| :--- | :--- | :--- | :--- |
| P1 | 0 | 8 | 10 |
| P2 | 1 | 2 | 1 |
| P3 | 2 | 2 | 2 |
| P4 | 3 | 2 | 1 |
| P5 | 4 | 1 | 2 |

**Expected Behavior:**
- In **Priority Scheduling**, P1 (lowest priority 10) will wait until every other process finishes. If new high-priority processes keep arriving, P1 may never execute (**Starvation**).

---

### ⚪ Scenario D: Input Validation Case
**Objective:** To test the system’s robustness against invalid user inputs.

**Test Data:**
- **Arrival Time:** `-5` (Negative value)
- **Burst Time:** `0` (Zero value)
- **Process ID:** `[Empty]` or `Duplicate ID`

**Expected Behavior:**
- The system should display a **red error message** and refuse to add these processes to the table, ensuring data integrity.