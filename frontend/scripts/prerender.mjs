import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const distDir = path.resolve(__dirname, '../dist');
const indexPath = path.join(distDir, 'index.html');

if (!fs.existsSync(indexPath)) {
  console.error("dist/index.html does not exist. Please run vite build first.");
  process.exit(1);
}

const originalHtml = fs.readFileSync(indexPath, 'utf-8');
const currentYear = new Date().getFullYear();

// Build pre-rendered HTML payload for search engines & instant FCP
const preRenderedApp = `
<div class="flex flex-col min-h-screen bg-slate-100 font-sans max-w-[100vw] overflow-x-hidden">
  <!-- Persistent Beta Legal Notice -->
  <div class="bg-amber-500 text-amber-950 px-4 py-2 text-xs font-semibold flex items-center justify-center gap-2 border-b border-amber-600 shadow-xs z-40 text-center flex-wrap">
    <span class="bg-amber-950 text-amber-100 text-[10px] uppercase font-black px-1.5 py-0.5 rounded tracking-wider shadow-2xs">BETA</span>
    <span>Under legal review. Do not rely on this system for actual legal proceedings without independent verification from a qualified advocate.</span>
  </div>

  <!-- Header -->
  <header class="bg-legal-900 text-white border-b border-legal-800 sticky top-0 z-30 shadow-md">
    <div class="bg-amber-600/90 text-amber-50 px-4 py-1.5 text-xs flex items-center justify-between text-center font-medium">
      <div class="flex-1 flex items-center justify-center gap-1.5">
        <span>Legal information, not legal advice. Always consult a licensed Advocate of the Bar Council for formal representation.</span>
      </div>
      <a href="tel:15" class="bg-red-700 hover:bg-red-800 text-white px-2.5 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider ml-2 flex items-center gap-1 shadow-sm">
        <span>Emergency 15</span>
      </a>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
      <a href="/" class="flex items-center gap-3 group focus:outline-none focus:ring-2 focus:ring-emerald-400 rounded-lg p-1" aria-label="LawerAI Home">
        <div class="w-10 h-10 rounded-lg bg-legal-800 border border-legal-700 flex items-center justify-center text-emerald-400 shadow-inner">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1ZM2 16 5 8 8 16c-.87.65-1.92 1-3 1s-2.13-.35-3-1ZM7 21h10M12 3v18M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="font-serif font-bold text-lg sm:text-xl tracking-tight text-emerald-50">LawerAI</h1>
            <span class="hidden sm:inline-block font-urdu text-emerald-300 text-sm">قانون معاون</span>
          </div>
          <p class="text-[11px] text-legal-300 font-sans">A Project by Maverick Tech Ventures</p>
        </div>
      </a>

      <div class="flex items-center gap-2 sm:gap-4">
        <a href="tel:+923273202419" class="hidden xl:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-legal-800/60 text-emerald-200 border border-legal-700/80 text-xs font-medium hover:text-white">
          <span>+923273202419</span>
        </a>
        <a href="mailto:ahmedmansoorrind1210@gmail.com" class="hidden 2xl:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-legal-800/60 text-emerald-200 border border-legal-700/80 text-xs font-medium hover:text-white">
          <span>ahmedmansoorrind1210@gmail.com</span>
        </a>
      </div>
    </div>
  </header>

  <!-- Breadcrumb Navigation -->
  <nav aria-label="Breadcrumb" class="bg-slate-50 border-b border-slate-200/80 px-4 sm:px-6 py-2">
    <ol class="flex items-center gap-1.5 text-xs text-slate-500 flex-wrap">
      <li class="flex items-center gap-1.5">
        <a href="/" class="hover:text-legal-800 font-medium">LawerAI</a>
      </li>
      <li class="flex items-center gap-1.5 font-semibold text-slate-800">
        <span>/</span>
        <span>Live Case Intake & Statutory Intelligence</span>
      </li>
    </ol>
  </nav>

  <!-- Main Content Showcase -->
  <main class="flex-1 max-w-7xl mx-auto px-4 sm:px-6 py-8 w-full">
    <section class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8 mb-8">
      <h2 class="text-xl sm:text-2xl font-serif font-bold text-slate-900 mb-3">
        Pakistani Statutory Jurisprudence & Guided Case Intake
      </h2>
      <p class="text-sm text-slate-600 leading-relaxed max-w-3xl mb-6">
        LawerAI (by Maverick Tech Ventures) combines authoritative statutory grounding with multi-turn legal reasoning across the Pakistan Penal Code (PPC 1860), Code of Criminal Procedure (CrPC 1898), Code of Civil Procedure (CPC 1908), Constitution of Pakistan (1973), and provincial family and rent statutes.
      </p>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
        <div class="p-4 rounded-xl border border-slate-200 bg-slate-50">
          <strong class="block text-slate-900 font-bold mb-1">PPC Section 489-F (Cheque Dishonour)</strong>
          <p class="text-slate-600">Cognizable criminal prosecution for dishonestly issued cheques with summary suit remedies under Order 37 CPC.</p>
        </div>
        <div class="p-4 rounded-xl border border-slate-200 bg-slate-50">
          <strong class="block text-slate-900 font-bold mb-1">CrPC Section 22-A / 22-B (Ex-Officio Justice of Peace)</strong>
          <p class="text-slate-600">Judicial petition before the Sessions Judge when police refuse registration of an FIR under Section 154 CrPC.</p>
        </div>
        <div class="p-4 rounded-xl border border-slate-200 bg-slate-50">
          <strong class="block text-slate-900 font-bold mb-1">CPC Order 39 Rules 1 & 2 (Temporary Injunctions)</strong>
          <p class="text-slate-600">Urgent stay orders on property encroachment, preservation of status quo, and interim relief.</p>
        </div>
      </div>
    </section>
  </main>

  <!-- Global Footer -->
  <footer class="bg-slate-900 text-slate-300 border-t border-slate-800 text-xs mt-auto">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-10 lg:py-12">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-10">
        <div>
          <span class="font-serif font-bold text-lg text-white">LawerAI</span>
          <p class="text-slate-400 text-xs mt-2 leading-relaxed">
            AI-augmented Pakistani statutory jurisprudence, structured case intake, and verified legal aid directories. Made by Maverick Tech Ventures.
          </p>
        </div>
        <div>
          <h4 class="font-semibold text-white uppercase text-[11px] mb-3">Statutory Law Corpus</h4>
          <ul class="space-y-1.5 text-slate-400">
            <li>Pakistan Penal Code 1860</li>
            <li>Code of Criminal Procedure 1898</li>
            <li>Code of Civil Procedure 1908</li>
            <li>Constitution of Pakistan 1973</li>
          </ul>
        </div>
        <div>
          <h4 class="font-semibold text-white uppercase text-[11px] mb-3">Direct Contact</h4>
          <p class="text-slate-400">Phone: <a href="tel:+923273202419" class="text-emerald-400">+923273202419</a></p>
          <p class="text-slate-400 mt-1">Email: <a href="mailto:ahmedmansoorrind1210@gmail.com" class="text-emerald-400">ahmedmansoorrind1210@gmail.com</a></p>
        </div>
        <div>
          <h4 class="font-semibold text-white uppercase text-[11px] mb-3">Compliance & Sitemaps</h4>
          <p class="text-slate-400"><a href="/sitemap.xml" class="hover:text-emerald-400">XML Sitemap</a> • <a href="/robots.txt" class="hover:text-emerald-400">Robots.txt</a></p>
        </div>
      </div>
      <div class="pt-6 border-t border-slate-800 text-slate-500 text-[11px]">
        © ${currentYear} LawerAI. Made by Maverick Tech Ventures. All rights reserved.
      </div>
    </div>
  </footer>
</div>
`;

// Inject into <div id="root">
const serverRenderedHtml = originalHtml.replace(
  '<div id="root"></div>',
  `<div id="root">${preRenderedApp}</div>`
);

fs.writeFileSync(indexPath, serverRenderedHtml, 'utf-8');
console.log(`[SSR Pre-render] Successfully rendered server-side DOM into dist/index.html`);

// Also generate pre-rendered static routes for deep crawler paths
const routes = ['statutes', 'directory', 'emergency'];
for (const route of routes) {
  const routeDir = path.join(distDir, route);
  if (!fs.existsSync(routeDir)) {
    fs.mkdirSync(routeDir, { recursive: true });
  }
  const routeHtml = serverRenderedHtml.replace(
    'https://lawerai.vercel.app/',
    `https://lawerai.vercel.app/${route}`
  );
  fs.writeFileSync(path.join(routeDir, 'index.html'), routeHtml, 'utf-8');
  console.log(`[SSR Pre-render] Successfully rendered static route: dist/${route}/index.html`);
}
