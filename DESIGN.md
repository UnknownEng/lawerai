# Design System & UI Guidelines — LawerAI
*A project by Maverick Tech Ventures*
*Contact: +923273202419 | ahmedmansoorrind1210@gmail.com*

## 1. Brand Identity & Principles
**LawerAI** (Made by Maverick Tech Ventures) conveys authority, clarity, rapid responsiveness, and unwavering trust. The visual aesthetic is modern, clean, and accessibility-first.

- **Primary Brand Theme**: Deep Emerald Green (`#064e3b` / `#0f766e`) and Slate (`#0f172a`), accented with warm gold/amber for statutory highlights and legal emphasis.
- **Tone**: Professional, dignified, reassuring, and precise.

---

## 2. Color Palette & Accessibility Tokens
All color combinations strictly comply with WCAG 2.1 AA (contrast ratio >= 4.5:1 for body text, >= 3:1 for large headings and interactive components).

### Primary Colors
- **Brand Primary 900**: `#064e3b` (Deep Forest Emerald — Headers, primary buttons)
- **Brand Primary 800**: `#065f46` (Hover states)
- **Brand Primary 600**: `#0d9488` (Active accents, focus rings)
- **Brand Accent 500**: `#d97706` (Amber / Gold — Important warnings & legal badges)

### Neutral Scale
- **Background Root**: `#f8fafc` (Slate 50 — High readability, soft on eyes)
- **Surface / Card Background**: `#ffffff` (Pure White)
- **Border Subtle**: `#e2e8f0` (Slate 200)
- **Text Muted**: `#475569` (Slate 600)
- **Text Headings & Body**: `#0f172a` (Slate 900)

### Feedback & Status Tokens
- **Success Surface**: `#f0fdf4` (Emerald 50)
- **Success Border**: `#86efac` (Emerald 300)
- **Success Text**: `#166534` (Emerald 800)
- **Error Surface**: `#fef2f2` (Red 50)
- **Error Border**: `#fca5a5` (Red 300)
- **Error Text**: `#991b1b` (Red 800)
- **Warning Surface**: `#fffbeb` (Amber 50)
- **Warning Text**: `#92400e` (Amber 800)

---

## 3. Typography Scale & Hierarchy
System font stack prioritizing crisp legibility across macOS, Windows, iOS, and Android:
`font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";`

| Level | Size (rem / px) | Weight | Line Height | Usage |
| :--- | :--- | :--- | :--- | :--- |
| **H1** | 2.25rem (36px) / 2.75rem (44px) on desktop | Bold (700) | 1.2 | Single primary page title |
| **H2** | 1.75rem (28px) / 2.0rem (32px) on desktop | SemiBold (600) | 1.25 | Major sections (Intake, Directory, FAQ) |
| **H3** | 1.25rem (20px) / 1.5rem (24px) on desktop | SemiBold (600) | 1.3 | Cards, modal titles, statutory sections |
| **Body Large** | 1.125rem (18px) | Normal (400) | 1.5 | Hero subtext, lead paragraphs |
| **Body Base** | 1.0rem (16px) | Normal (400) | 1.5 | Primary reading copy, form fields, chat |
| **Caption / Small** | 0.875rem (14px) | Medium (500) | 1.4 | Badges, timestamps, footer copy, meta tags |

---

## 4. Layout, Spacing & Responsive Breakpoints
- **Container Max-Width**: `max-w-7xl` (1280px) centered with `px-4 sm:px-6 lg:px-8`.
- **Breakpoints**:
  - `sm`: 640px (Small tablets / large phones landscape)
  - `md`: 768px (Tablets portrait — desktop navigation threshold)
  - `lg`: 1024px (Laptops / desktops)
  - `xl`: 1280px (Standard desktops)
  - `2xl`: 1536px (Widescreen displays)

---

## 5. Component Guidelines

### 5.1 Clickable Logo & Header
- **Desktop**: Left-aligned brand mark + logo linking directly to `/`. Right-aligned navigation items (`Statutes`, `Directory`, `FAQ`, `Emergency Help`), phone contact trigger, and CTA.
- **Mobile (< 768px)**: Logo + hamburger button. When tapped, opens an accessible slide-over drawer with full navigation, direct phone link (`tel:`), direct email link (`mailto:`), and legal actions.

### 5.2 Interactive Contact Buttons
- **Phone Button**: Displays international formatted number (`+923273202419`) wrapping `<a href="tel:+923273202419">` with phone icon.
- **Email Button**: Displays official support address (`ahmedmansoorrind1210@gmail.com`) wrapping `<a href="mailto:ahmedmansoorrind1210@gmail.com">` with envelope icon.

### 5.3 Feedback Components
- **Success Banner**: Emerald background, check-circle icon, bold title, descriptive confirmation text, dismiss button.
- **Error Banner**: Red background, alert-triangle icon, bold title, actionable remedy text, retry action.

### 5.4 Breadcrumbs
- Visual bar with home icon -> category -> current page.
- Semantic `<nav aria-label="Breadcrumb">` wrapping an ordered list `<ol>`.

### 5.5 Custom 404 Page
- Prominent 404 badge.
- Clear title: "Page Not Found".
- Helpful explanatory message explaining that the URL may have moved or been typed incorrectly.
- Actionable buttons: "Return to Home", "Browse Statutes", "Legal Directory".
- Quick statutory search input embedded directly on the page.

### 5.6 Footer
- Brand summary and mission statement.
- Four distinct link columns:
  1. **Legal Intelligence**: PPC, CrPC, Family Law, Constitutional Petitions.
  2. **Resources**: Directory, FAQ, Evidence Checklists, Emergency Legal Help.
  3. **Company & Compliance**: About LawerAI, Terms of Service, Privacy Policy, XML Sitemap.
  4. **Direct Contact**: Clickable Phone (`+923273202419`), Clickable Email (`ahmedmansoorrind1210@gmail.com`), Maverick Tech Ventures.
- Dynamic copyright bar: `© {new Date().getFullYear()} LawerAI. Made by Maverick Tech Ventures. All rights reserved.`
