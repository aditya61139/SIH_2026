# Phase 06 Plan: Swadesi & Patriotic UI Overhaul

## Objective
Transform the **VoxSentinalX** web dashboard into an authentic, dignified, clean, and patriotic **Swadesi** design system for the Smart India Hackathon (SIH 2026 Problem Statement ID: 26104). The new visual language replaces dark cyberpunk matrix aesthetics with a warm Indian Khadi/Parchment backdrop, deep Saffron (Bhagwa/Keshariya) primary actions, India/Tiranga Green verification indicators, Ashoka Slate typography, and crisp white surfaces.

---

## Exact Reference Palette Mapping

| UI Element | Color Code | Swadesi Role / Token |
| :--- | :--- | :--- |
| **Page Background** | `#FDFBF7` | Warm Khadi / Ivory Parchment |
| **Sidebar / Secondary Background** | `#F8F5EF` | Soft Linen Ivory |
| **Cards / Panels / Modals / Inputs** | `#FFFFFF` | Crisp White Surface |
| **Primary Headings / Important Values** | `#1E293B` | Ashoka Deep Slate / Charcoal Navy |
| **Secondary Text / Metadata** | `#64748B` | Muted Slate |
| **Disabled / Inactive Text** | `#94A3B8` | Cool Grey |
| **Primary Buttons** | `#C2410C` | Bhagwa / Deep Saffron |
| **Button Hover** | `#9A3412` | Rich Terracotta / Deep Saffron |
| **Active Tab / Active Navigation** | `#C2410C` | Saffron Navigation Accent |
| **Active/Selected Background** | `#FFF1E8` | Light Saffron Tint |
| **Active Audio Waveform** | `#C2410C` | Saffron Live Waveform |
| **Inactive Waveform / Audio Track** | `#94A3B8` | Muted Track Line |
| **Verified Waveform / Match Found** | `#15803D` | India Green / Tiranga Green |
| **Backend Connected / Safe (Low Risk)**| `#15803D` | India Green |
| **Suspicious / Medium Risk** | `#D97706` | Golden Ochre / Warm Amber |
| **High Risk / Cloned Voice / Critical**| `#DC2626` | Crimson Threat Alert |
| **Borders** | `#E7E2DA` | Warm Sandstone Border |
| **Dividers** | `#ECE8E1` | Soft Cream Divider |

---

## Execution Tasks

### Task 1: Tailwind Configuration & Global Theme Engine
- Update [`frontend/tailwind.config.js`](file:///p:/VoxSentinalX/frontend/tailwind.config.js):
  - Configure `swadesi` color tokens (`page`, `secondary`, `card`, `heading`, `text`, `muted`, `saffron`, `saffronHover`, `saffronLight`, `green`, `amber`, `danger`, `border`, `divider`).
  - Add warm box shadows (`shadow-swadesi-sm`, `shadow-swadesi-md`, `shadow-swadesi-saffron`).
- Update [`frontend/src/index.css`](file:///p:/VoxSentinalX/frontend/src/index.css):
  - Set root background `#FDFBF7` and text `#1E293B`.
  - Add modern `accent-color: #C2410C`.
  - Add elegant warm scrollbar (`#94A3B8` on `#F8F5EF`).
  - Add tricolor micro-gradient line utility (`.tiranga-stripe`).
  - Clean card utilities (`.swadesi-card`, `.swadesi-panel`).
- Update [`frontend/src/App.tsx`](file:///p:/VoxSentinalX/frontend/src/App.tsx):
  - Set default theme to light Swadesi layout (`bg-[#FDFBF7] text-[#1E293B]`).

### Task 2: Navigation & Hero Branding
- Update [`frontend/src/components/Navbar.tsx`](file:///p:/VoxSentinalX/frontend/src/components/Navbar.tsx):
  - Add top Tiranga micro-stripe (Saffron-White-Green).
  - Ashoka-inspired emblem and "VoxSentinalX" brand logo.
  - Saffron active navigation state (`text-[#C2410C] bg-[#FFF1E8] border-b-2 border-[#C2410C]`).
  - Backend connection pill: `#15803D` with pulsing dot.
- Update [`frontend/src/components/LandingView.tsx`](file:///p:/VoxSentinalX/frontend/src/components/LandingView.tsx):
  - Dignified SIH 2026 Bharat header badge.
  - Saffron primary button (`bg-[#C2410C] hover:bg-[#9A3412] text-white`).
  - Transform 8-vector forensic matrix into clean, high-appeal white cards with `#E7E2DA` borders.
  - Interactive threat testing sandbox in clean white card with Indic dialect scenario.

### Task 3: Real-Time Audio & Canvas Visualizers
- Update [`frontend/src/components/WaveformHeroVisualizer.tsx`](file:///p:/VoxSentinalX/frontend/src/components/WaveformHeroVisualizer.tsx):
  - Render frequency bars with Saffron (`#C2410C`) to India Green (`#15803D`) dynamic gradients on clean `#FFFFFF` / `#F8F5EF` canvas.
  - Subtle grid in `#ECE8E1`.
- Update [`frontend/src/lib/audioVisualizer.ts`](file:///p:/VoxSentinalX/frontend/src/lib/audioVisualizer.ts):
  - Active audio waveform: `#C2410C`.
  - Low Risk / Verified: `#15803D`.
  - Medium Risk: `#D97706`.
  - High Risk / Critical: `#DC2626`.
  - Canvas background: `#FFFFFF` with `#ECE8E1` grid lines.

### Task 4: Monitoring Console, Radar, and Gauge Overhaul
- Update [`frontend/src/components/RiskGauge.tsx`](file:///p:/VoxSentinalX/frontend/src/components/RiskGauge.tsx):
  - White card container with `#E7E2DA` border.
  - Gauge track in `#ECE8E1`.
  - Arc colors: `#15803D` (Low), `#D97706` (Moderate), `#DC2626` (High).
  - Risk typography in `#1E293B`.
- Update [`frontend/src/components/ForensicRadar.tsx`](file:///p:/VoxSentinalX/frontend/src/components/ForensicRadar.tsx):
  - 8-axis SVG chart with `#E7E2DA` grid polygons, `#1E293B` labels, `#C2410C` data stroke with soft translucent fill.
- Update [`frontend/src/components/LiveCallMonitor.tsx`](file:///p:/VoxSentinalX/frontend/src/components/LiveCallMonitor.tsx):
  - Clean white panels, Saffron primary monitoring button (`#C2410C`).
  - Active caller ratio and voiceprint separation indicators.
- Update [`frontend/src/components/DiagnosticFeed.tsx`](file:///p:/VoxSentinalX/frontend/src/components/DiagnosticFeed.tsx):
  - Clean status pills in Green (`#15803D`), Amber (`#D97706`), and Red (`#DC2626`).

### Task 5: File Analyzer, Modals & Settings
- Update [`frontend/src/components/FileAnalyzer.tsx`](file:///p:/VoxSentinalX/frontend/src/components/FileAnalyzer.tsx):
  - File upload box with `#F8F5EF` background, `#E7E2DA` dashed border.
  - Audio player and timeline scrub in Swadesi palette.
- Update [`frontend/src/components/CalibrationModal.tsx`](file:///p:/VoxSentinalX/frontend/src/components/CalibrationModal.tsx):
  - Modal surface in `#FFFFFF`, border `#E7E2DA`, record button `#C2410C`.
- Update [`frontend/src/components/AlertOverlay.tsx`](file:///p:/VoxSentinalX/frontend/src/components/AlertOverlay.tsx):
  - Crisp emergency overlay with `#DC2626` alert border.
- Update [`frontend/src/components/ModelTrainingSuite.tsx`](file:///p:/VoxSentinalX/frontend/src/components/ModelTrainingSuite.tsx) & [`SettingsPanel.tsx`](file:///p:/VoxSentinalX/frontend/src/components/SettingsPanel.tsx):
  - Clean cards and forms with Saffron focus rings.

---

## Verification Plan
1. **Frontend Build**:
   ```cmd
   cmd.exe /c "npm run build"
   ```
   Zero TypeScript or Vite compilation errors.
2. **Visual Verification**:
   - Page background strictly `#FDFBF7`.
   - Cards and modals strictly `#FFFFFF`.
   - Primary actions and active tabs strictly `#C2410C`.
   - Verified/safe states strictly `#15803D`.
   - Headings strictly `#1E293B`.
   - Subtext strictly `#64748B`.
   - Borders strictly `#E7E2DA`.
3. **Automated Backend Compatibility**:
   ```cmd
   & "C:\Users\adity\AppData\Local\Programs\Python\Python311\python.exe" -m pytest tests/ -v
   ```
   All 22 backend tests continue passing seamlessly.
