# Coding Rules & Technical SEO Standards — LawerAI
*A project by Maverick Tech Ventures*
*Contact: +923273202419 | ahmedmansoorrind1210@gmail.com*

## 1. General Engineering Principles
- **No Incomplete Implementations**: No mock TODOs, fake buttons, unhandled edge cases, or placeholder text ("Lorem Ipsum", "Coming soon").
- **Strict Semantic HTML**: Use appropriate landmark elements (`<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<footer>`).
- **Clean Architecture & Separation of Concerns**: Keep business logic, UI presentation, and data-fetching distinct and modular.

---

## 2. Technical SEO Mandatory Rules

### Rule 2.1: Exactly One `<h1>` Per Page
- Each page MUST contain exactly one `<h1>` element representing the primary topic of the page.
- Subheadings must follow strict descending order: `<h1>` -> `<h2>` -> `<h3>` -> `<h4>`. Never skip heading levels for visual styling; use CSS classes for typography size.

### Rule 2.2: Unique Titles & Meta Descriptions
- Every page must have a distinct `<title>` (50–60 characters) following the pattern:
  `Primary Keyword / Page Topic — LawerAI`
- Every page must have a tailored `<meta name="description">` (150–160 characters) summarizing page intent with strong call-to-action.

### Rule 2.3: Canonical Tags & Robots Directives
- Every public page must contain a self-referencing absolute canonical tag:
  `<link rel="canonical" href="https://lawerai.vercel.app/[route]" />`
- Administrative, authenticated, or temporary error pages must explicitly contain:
  `<meta name="robots" content="noindex, nofollow" />`
- Public pages must never be blocked by `robots.txt` or inadvertent `noindex` headers.

### Rule 2.4: Structured Data (Schema.org)
- FAQ sections must be paired with valid JSON-LD `FAQPage` schema.
- Breadcrumbs must output Schema.org `BreadcrumbList` markup.
- Site entity must output `Organization` / `WebSite` schema.

### Rule 2.5: Image Alt Text & Modern Formats
- Every `<img>` tag must include a descriptive, meaningful `alt` attribute.
- Purely decorative images must have `alt=""` and `aria-hidden="true"`.
- All images must be converted to `.webp` or `.svg` format and compressed to under 100KB.
- Every image must specify explicit `width` and `height` (or CSS `aspect-ratio`) to prevent Cumulative Layout Shift (CLS).

### Rule 2.6: Link Architecture & Orphan Prevention
- All internal navigation links must be crawlable anchor tags (`<a href="...">`).
- Do not use `onClick` handlers on `<div>` or `<span>` elements for page navigation.
- Never link to `#` or empty strings.
- All deep pages (e.g. statutes, legal directory, privacy policy) must be linked from either the primary navigation, breadcrumbs, or footer.

---

## 3. UI/UX & Responsive Design Rules

### Rule 3.1: Zero Horizontal Scrolling & Overflow Containment
- No horizontal scrolling is allowed on any viewport width (320px to 4K).
- Enforce `overflow-x: clip` or `hidden` on root containers.
- Always apply `min-w-0` to flex child items containing text or media to prevent flex container overflow.
- Avoid fixed pixel widths (`width: 600px`); use relative percentages or max-widths (`max-w-xl w-full`).

### Rule 3.2: Mobile Navigation
- Provide an accessible mobile menu drawer/overlay for viewports `< 768px` (md breakpoint).
- Mobile menu must support:
  - Toggle button with `aria-expanded` and `aria-label`.
  - ESC key to close.
  - Backdrop click to close.
  - Automatic closure upon navigating to a link.

### Rule 3.3: Interactive Contact Protocols
- Phone numbers must be interactive links formatted as: `<a href="tel:+923273202419">`.
- Email addresses must be interactive links formatted as: `<a href="mailto:ahmedmansoorrind1210@gmail.com">`.
- Brand logo in header and footer must link directly to `/`.

### Rule 3.4: Dynamic Copyright Year
- Never hardcode the copyright year. Always compute it dynamically:
  `© {new Date().getFullYear()} LawerAI. Made by Maverick Tech Ventures. All rights reserved.`

### Rule 3.5: Feedback States (Success & Error Messages)
- Every user submission or mutation (intake submission, lawyer inquiry, statute search) must provide clear, accessible feedback:
  - Success: Visible green alert/toast with affirmative confirmation.
  - Error: Visible red alert/toast with clear explanation of what failed and how to remediate.

---

## 4. Performance & Core Web Vitals Rules
- Target sub-2s total page load time across standard mobile connections.
- Keep total JavaScript bundle size minimal; tree-shake unused icons and libraries.
- Avoid layout thrashing; batch DOM operations and use CSS transitions instead of JS animation loops.
