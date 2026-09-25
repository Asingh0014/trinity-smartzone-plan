# Trinity: Student Wired 2026 port rollout

Scope: LAN1–4 on in-room **H510** and **H550** APs in `Default Zone` move to the
**Student Wired 2026** Ethernet port profile. LAN5 stays on **Default Trunk Port(WAN)**.

- Change window: **2026-09-26**
- Controller: SmartZone, `Default Zone`
- APs in scope: 396 (389 H510, 7 H550)

## Decisions

- **Dorothy** (Ground Floor, L1–L4, 106 H510s) moves **off Eduroam** to Student Wired 2026.
- **Switch configuration** is out of scope. The Student Wired 2026 VLAN is already trunked to the AP switch ports.

## Checking scripts

Both scripts only read settings. Neither changes anything on the controller.

```bash
export SZ_USERNAME=script
export SZ_PASSWORD='...'
python3 view_ap_port_config_trinity.py     # AP-level overrides     -> smartzone.csv
python3 view_apgroup_port_overrides.py     # AP group vs zone ports -> apgroup_port_overrides.csv
```

---

## Phase 0: Before the change window

- [x] Decide on Dorothy: it's moving to Student Wired 2026
- [x] Check the Student Wired 2026 profile: confirmed by the pilot
- [x] Check the switch VLANs: out of scope, already configured
- [x] Back up the SmartZone configuration (**Administration → Backup & Restore**)
- [x] Book the change window: 2026-09-26
- [ ] **Record the current state:** run both scripts, export the AP list, and keep the files with the backup

## Phase 1: Pilot ✅

- [x] `20:58:69:31:58:D0` (Clarke CK1B04 / CL004) set to Student Wired 2026 at AP level and tested successfully

## Phase 2: Zone-level change

Go to **Default Zone → Configure → AP Model-Specific Configuration**.

- [ ] **H510:** LAN1–4 → **Student Wired 2026**, leave LAN5 on Default Trunk Port(WAN)
- [ ] **H550:** LAN1–4 → **Student Wired 2026**, leave LAN5 on Default Trunk Port(WAN)
- [ ] Test one room per building:
  - [ ] Behan (56 APs)
  - [ ] Bishops (28)
  - [ ] Clarke (49)
  - [ ] Cowan (59)
  - [ ] Gourlay (25)
  - [ ] Jeopardy H510 (49)
  - [ ] Jeopardy H550 (7)

## Phase 3: Remove the AP group overrides

For each group, go to **Configure → AP Model-Specific Configuration → H510** and untick **Override zone config**.

| Done | AP group | H510s | Current LAN1–4 |
|---|---|---|---|
| [ ] | TC-Dorothy Ground Floor | 2 | Eduroam |
| [ ] | TC-Dorothy L1 | 26 | Eduroam |
| [ ] | TC-Dorothy L2 | 26 | Eduroam |
| [ ] | TC-Dorothy L3 | 26 | Eduroam |
| [ ] | TC-Dorothy L4 | 26 | Eduroam |
| [ ] | TC-Dorothy Basement | 0 | Eduroam (clean-up only) |
| [ ] | TC-Dorothy L1 IoT | 0 | Eduroam (clean-up only) |
| [ ] | default | 1 | Student Wired 2026 |

- [ ] Test one room on each Dorothy floor: Ground, L1, L2, L3, L4

## Phase 4: Remove the AP-level override

- [ ] `20:58:69:31:58:D0` (Clarke CK1B04): go to **Configure → Port Settings** and untick **Override Group Config**
- [ ] Re-test the pilot room. It should still work, now with the settings coming from the zone.

## Phase 5: Fix the stray APs

- [ ] `20:58:69:30:F0:F0` (Clarke 1st Floor CL124, blank AP group): move it into **TC-Clarke**
- [ ] `94:BF:C4:36:DC:E0` (no description, in `default`): find out what it is. If it's an in-room AP, move it into the correct TC group.

## Phase 6: Check the results

- [ ] `view_apgroup_port_overrides.py`: both zone rows show Student Wired 2026, and every group shows `Overrides Zone = No`
- [ ] `view_ap_port_config_trinity.py`: no H510/H550 with an AP-level override
- [ ] AP list: all 396 H510/H550s are online with their configuration up to date
- [ ] Watch for complaints over the next day, especially from Dorothy (previously Eduroam) and the rooms previously on the Guest profile

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

## Out of scope: other AP-level overrides

These are not H510/H550 and are left as they are. They have LAN1/LAN2 set to Default Trunk Port(WAN) at AP level.

| AP MAC | Model | Description | AP group |
|---|---|---|---|
| `34:20:E3:0E:1F:80` | R750 | Evan Burge – Library North | TC-Evan Burge |
| `34:20:E3:14:EE:00` | R750 | Bishops Hallway Lvl 1 North | TC-Bishops |
| `44:1E:98:17:71:80` | R710 | Evan Burge Lecture Theatre | TC-Evan Burge LBS |
| `58:FB:96:19:29:10` | R850 | Gateway B.18 – Music Room 1 | TC-Gateway |
| `70:CA:97:0C:89:70` | R710 | Behan Ground Floor – Hallway North | TC-Behan |
| `70:CA:97:0C:89:C0` | R710 | Evan Burge Lecture Theatre (offline) | TC-Evan Burge |
