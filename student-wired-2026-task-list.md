# Trinity: Student Wired 2026 port rollout

Scope: LAN1–4 on in-room **H510** and **H550** APs in `Default Zone` move to the
**Student Wired 2026** Ethernet port profile. LAN5 stays on **Default Trunk Port(WAN)**.

- Change window: **2026-09-26** (completed)
- Controller: SmartZone, `Default Zone`
- APs in scope: 396 (389 H510, 7 H550)

## Status (updated 2026-09-26)

| Phase | Status |
|---|---|
| 0: Before the change window | ✅ Complete (except recording the current state beforehand) |
| 1: Pilot | ✅ Complete |
| 2: Zone-level change | ✅ Complete and tested |
| 3: Remove AP group overrides | ✅ Complete and tested |
| 4: Remove AP-level override | ✅ Complete and tested |
| 5: Stray APs | ✅ Complete |
| 6: Check results | 🟡 AP list checked. Script checks and the day-after monitoring are still open. |

WLAN groups were also moved to **NEG SEG 2026** in the same window (see below).

## Decisions

- **Dorothy** (Ground Floor, L1–L4, 106 H510s) moves **off Eduroam** to Student Wired 2026.
- **Switch configuration** is out of scope. The Student Wired 2026 VLAN is already trunked to the AP switch ports.
- **`94:BF:C4:36:DC:E0`** (H510 in `default`) is a **test AP** and stays in the `default` AP group and WLAN group.
- **`58:FB:96:18:F1:40`** (R850, Gateway Auditorium) is **intentionally** on the **NEG SEG 2026 - Cafe** WLAN group.

## Checking scripts

Both scripts only read settings. Neither changes anything on the controller.

```bash
export SZ_USERNAME=script
export SZ_PASSWORD='...'
python3 view_ap_port_config_trinity.py     # AP-level overrides        -> smartzone.csv
python3 view_apgroup_port_overrides.py     # AP group vs zone ports    -> apgroup_port_overrides.csv
python3 view_apgroup_wlan_groups.py        # WLAN group per AP group   -> apgroup_wlan_groups.csv
```

---

## Phase 0: Before the change window

- [x] Decide on Dorothy: it's moving to Student Wired 2026
- [x] Check the Student Wired 2026 profile: confirmed by the pilot
- [x] Check the switch VLANs: out of scope, already configured
- [x] Back up the SmartZone configuration (**Administration → Backup & Restore**)
- [x] Book the change window: 2026-09-26
- [ ] Record the current state with the scripts beforehand. Only the AP list was exported beforehand. The previous port settings are in the Rollback table below.

## Phase 1: Pilot ✅

- [x] `20:58:69:31:58:D0` (Clarke CK1B04 / CL004) set to Student Wired 2026 at AP level and tested successfully

## Phase 2: Zone-level change ✅

Go to **Default Zone → Configure → AP Model-Specific Configuration**.

- [x] **H510:** LAN1–4 → **Student Wired 2026**, leave LAN5 on Default Trunk Port(WAN)
- [x] **H550:** LAN1–4 → **Student Wired 2026**, leave LAN5 on Default Trunk Port(WAN)
- [x] Test one room per building:
  - [x] Behan (56 APs)
  - [x] Bishops (28)
  - [x] Clarke (49)
  - [x] Cowan (59)
  - [x] Gourlay (25)
  - [x] Jeopardy H510 (49)
  - [x] Jeopardy H550 (7)

## Phase 3: Remove the AP group overrides ✅

For each group, go to **Configure → AP Model-Specific Configuration → H510** and untick **Override zone config**.

| Done | AP group | H510s | LAN1–4 before |
|---|---|---|---|
| [x] | TC-Dorothy Ground Floor | 2 | Eduroam |
| [x] | TC-Dorothy L1 | 26 | Eduroam |
| [x] | TC-Dorothy L2 | 26 | Eduroam |
| [x] | TC-Dorothy L3 | 26 | Eduroam |
| [x] | TC-Dorothy L4 | 26 | Eduroam |
| [x] | TC-Dorothy Basement | 0 | Eduroam (clean-up only) |
| [x] | TC-Dorothy L1 IoT | 0 | Eduroam (clean-up only) |
| [x] | default | 1 | Student Wired 2026 |

- [x] Test one room on each Dorothy floor: Ground, L1, L2, L3, L4

## Phase 4: Remove the AP-level override ✅

- [x] `20:58:69:31:58:D0` (Clarke CK1B04): go to **Configure → Port Settings** and untick **Override Group Config**
- [x] Re-test the pilot room. It still works, now with the settings coming from the zone.

## Phase 5: Fix the stray APs ✅

- [x] `20:58:69:30:F0:F0` (Clarke 1st Floor CL124, blank AP group): moved into **TC-Clarke**
- [x] `94:BF:C4:36:DC:E0` (no description, in `default`): confirmed as a **test AP**, so no change

## Phase 6: Check the results

- [ ] `view_apgroup_port_overrides.py`: both zone rows show Student Wired 2026, and every group shows `Overrides Zone = No`
- [ ] `view_ap_port_config_trinity.py`: no H510/H550 with an AP-level override
- [x] AP list (export after the change): 395 of 396 H510/H550s online and up to date. The one offline AP, `94:BF:C4:03:0D:50` in TC-Gourlay, was already offline before the change. No AP went offline because of the change.
- [ ] Watch for complaints over the next day, especially from Dorothy (previously Eduroam) and the rooms previously on the Guest profile

---

## WLAN group change: NEG SEG 2026 (2026-09-26)

In the same window, the APs' WLAN groups were moved to **NEG SEG 2026**, and AP-level WLAN group
exceptions were cleared. This table compares AP list exports from before and after the change.
No AP has a 6GHz radio, so the 6GHz WLAN group is blank for every AP.

| AP group | Before (2.4GHz / 5GHz) | After (2.4GHz / 5GHz) |
|---|---|---|
| default | default | default *(unchanged; test AP)* |
| TC-200V | 200v | 200v *(unchanged)* |
| TC-Behan | Main - 802.11R Disabled | NEG SEG 2026 |
| TC-Bishops | Main - 802.11R Disabled | NEG SEG 2026 |
| TC-Bouverie Street | Bouverie | NEG SEG 2026 no Visitor |
| TC-Chapel | Main - 802.11R Disabled | NEG SEG 2026 |
| TC-Clarke | Main - 802.11R Disabled | NEG SEG 2026 |
| TC-Cowan | Main - 802.11R Disabled | NEG SEG 2026 |
| TC-Deanery | Deanery | NEG SEG 2026 - Deanery |
| TC-Dining Hall | Main - 802.11R Disabled | NEG SEG 2026 |
| TC-Dorothy Basement | P100 | NEG SEG 2026 |
| TC-Dorothy External | P100 | NEG SEG 2026 |
| TC-Dorothy Ground Floor | P100 | NEG SEG 2026 |
| TC-Dorothy L1 | P100 | NEG SEG 2026 |
| TC-Dorothy L1 IoT | P100 | NEG SEG 2026 |
| TC-Dorothy L2 | P100 | NEG SEG 2026 |
| TC-Dorothy L2 IoT | P100 | NEG SEG 2026 |
| TC-Dorothy L3 | default | NEG SEG 2026 |
| TC-Dorothy L3 IoT | P100 | NEG SEG 2026 |
| TC-Dorothy L4 | default | NEG SEG 2026 |
| TC-Dorothy L4 IoT | P100 | NEG SEG 2026 |
| TC-Evan Burge | Evan Burge | NEG SEG 2026 |
| TC-Gateway | Gateway | NEG SEG 2026 |
| TC-Gourlay | Main - 802.11R Disabled | NEG SEG 2026 |
| TC-Jeopardy | Main - 802.11R Disabled | NEG SEG 2026 |
| TC-Kitchen | Main - 802.11R Disabled | NEG SEG 2026 |
| TC-Leeper | Main - 802.11R Disabled / Leeper | NEG SEG 2026 |
| TC-OWL | Main - 802.11R Disabled | NEG SEG 2026 |
| TC-Summer House | Main - 802.11R Disabled / default | NEG SEG 2026 |

**AP-level WLAN group exceptions**

| AP MAC | Model | Location | Before | After |
|---|---|---|---|---|
| `18:7C:0B:1D:4D:F0` | H510 | Jeopardy – Tutor Flat 2nd Floor | SimonWiFi_RT380843 | NEG SEG 2026 (cleared) |
| `18:7C:0B:1D:4E:10` | H510 | Cowan – Tutor Flat CN119 | default | NEG SEG 2026 (cleared) |
| `34:FA:9F:1E:B6:90` | R710 | Evan Burge – ITS Office | Evan Burge - ITS | NEG SEG 2026 (cleared) |
| `58:FB:96:18:F1:40` | R850 | Gateway Auditorium Middle Right | Trinity Cafe | NEG SEG 2026 - Cafe (intended) |

**AP group moves**

| AP MAC | Model | Location | Before | After |
|---|---|---|---|---|
| `20:58:69:30:F0:F0` | H510 | Clarke 1st Floor CL124 | *(blank)* | TC-Clarke |
| `44:1E:98:17:71:80` | R710 | Evan Burge Lecture Theatre | TC-Evan Burge LBS | TC-Evan Burge |
| `70:CA:97:0C:7E:70` | R710 | Evan Burge Lecture Theatre | TC-Evan Burge LBS | TC-Evan Burge |

Result: every online AP (632 of 641) uses its AP group's WLAN group, apart from the intended Gateway Cafe AP. The 9 offline APs were already offline before the change.

---

## Rollback

Settings before the change. Reverting by hand, working from the zone level down, is quicker than restoring the backup.

| Where | Model | LAN1–4 before | LAN5 |
|---|---|---|---|
| Default Zone | H510 | Guest Access Anti-spoof disabled | Default Trunk Port(WAN) |
| Default Zone | H550 | Default Access Port | Default Trunk Port(WAN) |
| TC-Dorothy Basement / Ground Floor / L1 / L1 IoT / L2 / L3 / L4 | H510 | Eduroam (override ticked) | Default Trunk Port(WAN) |
| default group | H510 | Student Wired 2026 (override ticked) | Default Trunk Port(WAN) |
| AP `20:58:69:31:58:D0` | H510 | Student Main Campus Wired (override ticked; before the pilot) | Default Trunk Port(WAN) |

For the WLAN group values before the change, see the "Before" column of the WLAN group tables above.

## Out of scope: other AP-level port overrides

These are not H510/H550 and are left as they are. They have LAN1/LAN2 set to Default Trunk Port(WAN) at AP level.

| AP MAC | Model | Description | AP group |
|---|---|---|---|
| `34:20:E3:0E:1F:80` | R750 | Evan Burge – Library North | TC-Evan Burge |
| `34:20:E3:14:EE:00` | R750 | Bishops Hallway Lvl 1 North | TC-Bishops |
| `44:1E:98:17:71:80` | R710 | Evan Burge Lecture Theatre | TC-Evan Burge (was TC-Evan Burge LBS) |
| `58:FB:96:19:29:10` | R850 | Gateway B.18 – Music Room 1 | TC-Gateway |
| `70:CA:97:0C:89:70` | R710 | Behan Ground Floor – Hallway North | TC-Behan |
| `70:CA:97:0C:89:C0` | R710 | Evan Burge Lecture Theatre (offline) | TC-Evan Burge |
