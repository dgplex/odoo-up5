import { registry } from "@web/core/registry";
import { stepUtils } from "@web_tour/tour_utils";

/**
 * Layer 3 browser smoke tour for up5_nsvn_cylinder.
 *
 * Driven by TestCylinderTour.test_cylinder_tour (Python HttpCase).
 * Before the tour starts, Python commits one overdue cylinder so it is
 * visible in the DB session the tour uses.
 *
 * Steps verified:
 *   1. Navigate to Inventory app
 *   2. Open Cylinders menu → All Cylinders
 *   3. List view loads; overdue row is highlighted text-danger
 *   4. Open the overdue cylinder form
 *   5. Cylinder tab exists; overdue_days field is visible
 */
registry.category("web_tour.tours").add("up5_nsvn_cylinder_tour", {
    steps: () => [
        // ── Navigate to Inventory ──────────────────────────────────────────
        ...stepUtils.goToAppSteps("stock.menu_stock_root", "Open the Inventory app"),

        // ── Open Cylinders menu ───────────────────────────────────────────
        {
            trigger: "button[data-menu-xmlid='up5_nsvn_cylinder.up5_nsvn_cylinder_menu_root']",
            content: "Click the Cylinders top-level menu",
            run: "click",
        },
        {
            trigger: ".o-dropdown-item[data-menu-xmlid='up5_nsvn_cylinder.up5_nsvn_cylinder_menu_all']",
            content: "Click All Cylinders",
            run: "click",
        },

        // ── Verify list view ──────────────────────────────────────────────
        {
            trigger: ".o_list_view .o_data_row",
            content: "Cylinder list view loaded with at least one row",
        },
        {
            // decoration-danger="is_overdue" maps to Bootstrap text-danger on the <tr>
            trigger: ".o_list_view .o_data_row.text-danger",
            content: "Overdue cylinder row is highlighted red",
        },

        // ── Open the overdue cylinder ─────────────────────────────────────
        {
            trigger: ".o_list_view .o_data_row.text-danger .o_data_cell[name='name']",
            content: "Open the overdue cylinder form",
            run: "click",
        },

        // ── Verify form view + Cylinder tab ──────────────────────────────
        {
            trigger: ".o_form_view",
            content: "Stock lot form view is open",
        },
        {
            trigger: ".o_notebook .nav-link:contains('Cylinder')",
            content: "Click the Cylinder tab",
            run: "click",
        },
        {
            // overdue_days has invisible="not is_overdue" — this step fails if the
            // field is hidden, which would indicate the overdue status is wrong
            trigger: ".o_field_widget[name='overdue_days']",
            content: "Overdue Days field is visible (cylinder is correctly marked overdue)",
        },
    ],
});
