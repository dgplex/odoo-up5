# Claude Progress Log

## Current Verified State

- **Branch:** `19.0-add-harness-engineering-cla`
- **Last verified:** 2026-06-13
- **Environment:** conda env `odoo19` (Python 3.12) + PostgreSQL 17 + `odoo_dev` database ✅
- **Repo status:** `up5_nsvn_cylinder` module installed + Layers 1+2 passing — **Layer 3 pending**
- **Verification:**
  ```
  === Pre-flight ===        ✅
  === Layer 1 — Static Analysis ===   All checks passed!   ✅
  Layer 1 passed.
  === Layer 2 — Runtime Verification ===
  0 failed, 0 error(s) of 7 tests   ✅
  Layer 2 passed.
  === Layer 3 — System Confirmation (manual) ===  → PENDING browser smoke test
  ```
- **Tests (10/10):**
  - `test_overdue_cylinder` — 40-day dispatch, 30-day rental → overdue by 10 ✅
  - `test_not_overdue_cylinder` — 10-day dispatch, 30-day rental → not overdue ✅
  - `test_just_dispatched_not_overdue` — dispatched today → not overdue ✅
  - `test_no_customer_no_overdue` — no customer → all computed fields zero ✅
  - `test_dispatch_date_without_customer_no_overdue` — dispatch set, no customer → not overdue ✅
  - `test_gas_type_and_is_cylinder_on_product` — product template fields readable ✅
  - `test_rental_days_default_is_thirty` — default rental_days = 30 ✅
  - `test_cylinder_action_loads` (HttpCase) — action in DB, res_model=stock.lot ✅
  - `test_cylinder_fields_accessible_via_rpc` (HttpCase) — overdue fields over JSON-RPC ✅
  - `test_product_gas_type_readable_via_rpc` (HttpCase) — gas_type/is_cylinder over RPC ✅
- **verify.sh fix:** detect installed vs not-installed via psql and use `-u` vs `-i` accordingly (was a false "0 tests" on already-installed module)

## Next Steps

1. Finish `up5_nsvn_cylinder` implementation — run `./verify.sh up5_nsvn_cylinder`, paste output as evidence
2. Layer 3 smoke test: install module in browser, verify Cylinders menu and overdue highlighting
3. Update `feature_list.json` state to `passing` with evidence
4. Update CLAUDE.md Project Identity with `up5_nsvn_cylinder`

## Blockers

None.

---

### Sprint Contract: up5-nsvn-cylinder — NSVN MVP Cylinder Lifecycle Tracking

**Behavior (from feature_list.json):**
The up5_nsvn_cylinder module installs on Odoo 19; adds cylinder-specific fields to stock.lot (type, capacity, customer, dispatch date, rental period); computes overdue status and days-at-customer; shows a dedicated Cylinders list view under Inventory with overdue rows highlighted in red; ./verify.sh up5_nsvn_cylinder exits 0.

**In scope:**
- `product.template` extended with `is_cylinder` (Boolean) and `gas_type` (Selection)
- `stock.lot` extended with physical fields + customer tracking fields
- Computed fields: `expected_return_date`, `days_at_customer`, `is_overdue`, `overdue_days` — store=True
- stock.lot form extended with Cylinder tab
- product.template form extended with is_cylinder + gas_type
- Cylinders action + menu under Inventory, filtered to is_cylinder=True, overdue decoration-danger
- TransactionCase tests covering overdue, not-overdue, and two failure scenarios (no customer)
- `./verify.sh up5_nsvn_cylinder` exits 0

**Out of scope (explicit):**
- AI demand forecasting, route optimization, predictive maintenance
- MRP / manufacturing orders
- e-invoicing / accounting integration
- CRM pipeline
- Fleet management
- Any other NSVN phase beyond cylinder tracking
- Cylinder rental billing / subscription contracts

**Verification command:** `./verify.sh up5_nsvn_cylinder`

**Ambiguities resolved:**
- `rental_days` default: 30 days (industry standard return period in Vietnam)
- Overdue condition: `today > expected_return_date` (strictly after, not on the day)
- Customer filter: `is_company=True` domain on customer_id (B2B only — hospitals, factories)
- `cylinder_state` is manually set (not auto-computed from stock moves) for MVP simplicity
- No `ir.model.access.csv` needed — only extending existing models, not creating new ones

**Layer 3 smoke test result:** *(fill in after manual browser test)*
- Server started: pending — run `conda run -n odoo19 python odoo-bin -c odoo.conf`
- Module installed without error: ✅ (confirmed via `-i up5_nsvn_cylinder` install output)
- Critical path to exercise: Inventory → Cylinders → All Cylinders; open a cylinder form, check Cylinder tab; verify overdue row shows red
- Result: pending

---

## Session History

### Session 1 — 2026-06-13
- **Goal:** Set up harness files (CLAUDE.md, claude-progress.md, feature_list.json)
- **Completed:** CLAUDE.md with Odoo conventions and definition of done; claude-progress.md; feature_list.json
- **Evidence:** `git status` clean on branch `19.0`
- **Decisions made:** See [DECISIONS.md](DECISIONS.md)

### Session 2 — 2026-06-13
- **Goal:** Apply harness engineering lectures 01–05 to the project
- **Completed:**
  - Lecture 01: Added 5 failure modes → CLAUDE.md implicit conventions, verification gap rule
  - Lecture 02: Added `verify.sh` (feedback subsystem), surfaced `ruff.toml`
  - Lecture 03: Added Project Identity, ACID rules, Fresh Session Test gaps fixed, `NOTES.md` template
  - Lecture 04: Split CLAUDE.md 294→91 lines; created `odoo-conventions.md`, expanded `dev-environment.md`
  - Lecture 05: Added `DECISIONS.md`, restructured `claude-progress.md` with Next Steps + Blockers
  - Created `up5-docs/` and `up5-learning/` folder structures
- **Evidence:** All commits pushed to `origin/19.0-add-harness-engineering-cla`

### Session 3 — 2026-06-13
- **Goal:** Install PostgreSQL and initialise `odoo_dev` database (initialization phase completion)
- **Completed:**
  - PostgreSQL 17 installed via EDB installer
  - `odoo` role created with LOGIN SUPERUSER PASSWORD 'odoo'
  - `odoo_dev` database initialised (14 modules loaded)
  - `ruff` installed in `odoo19` conda env
  - `verify.sh` fixed: conda multi-line arg bug resolved, lint now skips core Odoo modules
  - `./verify.sh account` exits 0 — full pipeline green
- **Evidence:**
  ```
  === Pre-flight checks ===
    odoo-bin: ok
    PostgreSQL: ok
    Module path: ok (addons/account)

  === Lint: skipped (core Odoo module — ruff applies to up5_* modules only) ===

  === Tests: -i account ===
  ...
  Tests passed.

  === account: all checks passed ===
  ```
- **Decisions made:** Lint skips non-`up5_*` modules (core Odoo code not our responsibility to lint)
