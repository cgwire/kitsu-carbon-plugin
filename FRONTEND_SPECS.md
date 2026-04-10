# Carbon Tracking Plugin - Frontend Specifications

See [KITSU_PLUGIN_GUIDE.md](./KITSU_PLUGIN_GUIDE.md) for technology stack, code style, color palette, and Vite dev proxy conventions.

Additional dependencies: Lucide Vue Next (icons), vue-i18n (localization).

## Pinia Store (`stores/main.js`)

Central store using the options API (`state` + `actions`) fetching data from the main Zou API.

**State:**
- `taskTypes` — all task types from `GET /api/data/task-types`
- `openProductions` — all open productions from `GET /api/data/projects/open`
- `sequences` — sequences for current production from `GET /api/data/projects/:id/sequences`
- `episodes` — episodes for current production from `GET /api/data/projects/:id/episodes`
- `assetTypes` — asset types for current production from `GET /api/data/projects/:id/asset-types`

**Actions:**
- `init()` — fetches task types + open productions in parallel
- `setCurrentProduction(productionId)` — handles production change:
  - No productionId: clears sequences, episodes, asset types
  - TV show (`production_type === "tvshow"`): fetches episodes + asset types, clears sequences
  - Other: fetches sequences + asset types, clears episodes

## Views

### Studio View (`StudioFootprint.vue`)

Displayed when no `production_id` query parameter is set.

**Stat Cards (3 columns):**
1. **Total Studio Emissions** (Cloud icon) — `data.total_co2_kg`
2. **Weekly Average Emissions** (Calendar icon) — total CO2 divided by number of weeks between oldest production start date and latest production end date (from `store.openProductions`)
3. **Total Man-Days** (Users icon) — `data.total_man_days`

**Tabs:**
- **Matrix view** — productions x task types grid with color-coded values
- **Production breakdown** — horizontal bar chart sorted by emissions

**Data behaviors:**
- Task type columns sourced from `store.taskTypes` (falls back to carbon API data)
- Empty columns (all zero values) are hidden
- Info button (top-right) opens calculation modal

### Production View (`ProductionFootprint.vue`)

Displayed when `production_id` query parameter is set.

**Stat Cards (3 columns):**
1. **Total Project Emissions** (Cloud icon) — `data.total_co2_kg`
2. **Weekly Average Emissions** (Calendar icon) — total CO2 divided by number of weeks between the project `start_date` and `end_date` (from `store.openProductions`)
3. **Total Man-Days** (Users icon) — `data.total_man_days`

**Tabs:**
- **Matrix view** — task types grid with color-coded values
- **Step breakdown** — horizontal bar chart sorted by emissions

**Data behaviors:**
- Task type columns sourced from `store.taskTypes` (falls back to carbon API data)
- Empty columns (all zero values) are hidden

### Shared Components & Composables

Duplicated UI elements are extracted into reusable sub-components:

| Component | Purpose |
|-----------|---------|
| `FootprintHeader.vue` | Page header with title, subtitle, unit toggle, and info button |
| `StatCards.vue` | 3-column stat cards (total emissions, weekly average, man-days) |
| `ViewTabs.vue` | Matrix / breakdown tab switcher |
| `ImpactLegend.vue` | Color legend (low / medium / high impact), placed outside the scrollable table area |
| `InfoModal.vue` | Calculation explanation modal with "Read full documentation" PDF download link |
| `UnitToggle.vue` | kg/t unit toggle (`v-model`) |
| `DisclaimerNotice.vue` | Regulatory disclaimer about estimation accuracy and CNC obligations |

Shared logic lives in composables:

**`composables/useCarbon.js`:**
- Shared state: `unit`, `activeTab`, `showInfo` (with localStorage persistence)
- Formatting: `formatValue`, `formatValueOrDash`, `formatNumber`
- Impact helpers: `getImpactClass`, `getBarWidth`, `getPercent`
- Task type styling: `getTaskTypeColor`, `taskTypeHeaderStyle`, `taskTypeCellStyle`
- Escape key handler for modal dismissal

**`composables/useTheme.js`:**
- Reads `dark_theme` query param from the URL
- Returns `isDarkTheme` (boolean) and `themeClass` (`"dark-theme"` or `"light-theme"`)

### Router (`CarbonFootprint.vue`)

- Reads `production_id` from route query params
- Calls `store.init()` on mount
- Watches `productionId` and calls `store.setCurrentProduction()`
- Renders `ProductionFootprint` or `StudioFootprint` based on `production_id` presence
- Uses `createWebHashHistory` for static plugin serving
- On initial load, transfers real URL query params into hash-based route

## Calculation Modal

Explains how carbon is calculated. Shown on Info button click.

**Formula** (monospace font, card background):
```
Work Time  x  People  x  Carbon Factor
```
"Carbon Factor" displayed in green (`--accent-green`).

**Included factors** (2-column grid on desktop, 1-column on mobile, with icons):
| Icon | Factor |
|------|--------|
| Monitor | Workstation |
| Building2 | Building Energy |
| Zap | Electricity Mix |
| UtensilsCrossed | Meals |
| Cloud | Cloud & Infra |
| TrainFront | Commute |

**Documentation link:** "Read full documentation" button downloads the bundled PDF (`assets/carbon-emissions-calculating-emissions.pdf`). Visible only on mobile.

**Mobile behavior:** modal slides up from bottom (full width, rounded top corners), scrollable content with `max-height: 90vh`.

## Internationalization (i18n)

Uses `vue-i18n` in composition mode (`legacy: false`).

**Supported locales:** English (`en`, default), French (`fr`).

**Locale detection:** reads `?locale=` query param from the URL (set by Kitsu's `Plugin.vue` from the user's profile locale). Falls back to `en`.

**Translation files:** `locales/en.js` and `locales/fr.js` with nested keys under the `carbon` namespace (e.g., `carbon.stats.total_project_emissions`).

**Not localized (intentional):** `kgCO2e` / `tCO2e` unit labels (standardized scientific notation), task type names (come from the API).

## Theming

Uses CSS custom properties defined in `assets/theme.css`. Light theme is the default; dark theme activates via the `.dark-theme` class on `.carbon-tracking`.

**Theme detection:** reads `?dark_theme=true` query param from the URL (set by Kitsu's `Plugin.vue` based on user preference). Absence of the param defaults to light theme.

**Variable categories:**
- Backgrounds: `--bg-page`, `--bg-card`, `--bg-surface`, `--bg-row-odd`, `--bg-row-even`, `--bg-total-row`, `--bg-modal`, `--bg-overlay`, `--bg-disclaimer`
- Text: `--text-primary`, `--text-heading`, `--text-secondary`, `--text-tertiary`, `--text-muted`
- Borders: `--border-primary`, `--border-secondary`, `--border-light`, `--border-filter`
- Accents: `--accent-green`, `--accent-orange`, `--accent-red`
- Weekly change badges: `--change-up-bg`, `--change-down-bg`, `--change-neutral-bg`

## Responsive Layout

Breakpoint at `max-width: 768px`.

**Header:** wraps to two lines — title/subtitle on first line, unit toggle + info button on second line (spaced apart).

**Stat cards:** stack vertically (single column).

**Entity filters (Shots/Assets):** hidden on mobile.

**Matrix view:** reduced column widths and padding, horizontally scrollable.

**Breakdown view:** table transforms to card layout — table headers hidden, each row becomes name + value on one line with bar spanning full width below.

**Page scroll:** `.carbon-tracking` switches from fixed height (`100vh`, `overflow: hidden`) to natural height with `overflow-y: auto` on mobile.

## Persistence

- Unit preference saved to `localStorage` key `carbon-unit`
- Active tab saved to `localStorage` key `carbon-tab`

## Kitsu Integration

Kitsu embeds the plugin in an iframe via `Plugin.vue`. Query params passed to the plugin:
- `production_id` — current production (if any)
- `episode_id` — current episode (TV shows)
- `dark_theme` — `"true"` when Kitsu is in dark mode
- `locale` — 2-letter language code from user profile (e.g., `"fr"`, `"en"`)

## Frontend Files

| File | Purpose |
|------|---------|
| `frontend/src/main.js` | App entry, registers Pinia + Router + i18n, imports theme CSS |
| `frontend/src/router.js` | Vue Router with hash history + query param transfer |
| `frontend/src/lib/i18n.js` | vue-i18n setup, reads locale from URL query param |
| `frontend/src/stores/main.js` | Pinia store (Zou API data, options API) |
| `frontend/src/locales/en.js` | English translations |
| `frontend/src/locales/fr.js` | French translations |
| `frontend/src/assets/theme.css` | CSS custom properties for light/dark themes |
| `frontend/src/assets/carbon-emissions-calculating-emissions.pdf` | Documentation PDF (bundled as static asset) |
| `frontend/src/composables/useCarbon.js` | Shared state, formatting, and helpers |
| `frontend/src/composables/useTheme.js` | Theme detection from query param |
| `frontend/src/components/CarbonFootprint.vue` | Router component |
| `frontend/src/components/StudioFootprint.vue` | Studio-wide view |
| `frontend/src/components/ProductionFootprint.vue` | Per-production view |
| `frontend/src/components/FootprintHeader.vue` | Shared page header |
| `frontend/src/components/StatCards.vue` | Shared stat cards |
| `frontend/src/components/ViewTabs.vue` | Shared tab switcher |
| `frontend/src/components/ImpactLegend.vue` | Shared impact legend |
| `frontend/src/components/InfoModal.vue` | Shared calculation modal with PDF download |
| `frontend/src/components/UnitToggle.vue` | Shared unit toggle |
| `frontend/src/components/DisclaimerNotice.vue` | Regulatory disclaimer |
| `frontend/vite.config.js` | Vite config with dev proxy |
