# New Menu UI Starter

Use this starter when creating a new page/menu in frontend:

- `frontend/src/views/_starter/ErpMenuStarterView.vue`

## How to use

1. Copy the starter file into your target module folder (`master/`, `sales/`, `purchase/`, etc).
2. Rename component and page title.
3. Replace placeholder state/API with real implementation.
4. Keep the following structure:
   - `stack` root
   - `erp-head` section
   - form card
   - list card with `list-filters` and `table-wrap`

## Mandatory conventions

- Do not use inline style in template.
- Reuse global utility classes from `frontend/src/style.css`.
- Keep screen usable in both density modes:
  - Comfortable
  - Compact

## Final check before merge

- Header uses `erp-head` family classes.
- No duplicated page-specific header CSS.
- Empty/loading/error state is present.
- Table and filter remain readable on mobile and desktop.
