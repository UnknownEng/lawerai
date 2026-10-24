import React from 'react';
import { Home, ChevronRight, BookOpen, Users, ShieldAlert } from 'lucide-react';

export default function Breadcrumbs({ currentView = 'intake', onNavigate }) {
  const crumbs = [
    { id: 'home', label: 'LawerAI', icon: Home, href: '/' },
    {
      id: currentView,
      label:
        currentView === 'intake'
          ? 'Live Case Intake'
          : currentView === 'statutes'
          ? 'Statutory Law Library'
          : currentView === 'directory'
          ? 'Bar & Legal Aid Directory'
          : currentView === 'emergency'
          ? 'Emergency Crisis Helplines'
          : 'Legal Consultation',
      icon:
        currentView === 'statutes'
          ? BookOpen
          : currentView === 'directory'
          ? Users
          : currentView === 'emergency'
          ? ShieldAlert
          : null
    }
  ];

  return (
    <nav aria-label="Breadcrumb" className="bg-slate-50 border-b border-slate-200/80 px-4 sm:px-6 py-2">
      <ol className="flex items-center gap-1.5 text-xs text-slate-500 flex-wrap" itemScope itemType="https://schema.org/BreadcrumbList">
        {crumbs.map((crumb, idx) => {
          const isLast = idx === crumbs.length - 1;
          const Icon = crumb.icon;

          return (
            <li
              key={crumb.id}
              className="flex items-center gap-1.5"
              itemProp="itemListElement"
              itemScope
              itemType="https://schema.org/ListItem"
            >
              {idx > 0 && <ChevronRight className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" aria-hidden="true" />}
              
              {isLast ? (
                <span
                  className="font-semibold text-slate-800 flex items-center gap-1 truncate"
                  aria-current="page"
                  itemProp="name"
                >
                  {Icon && <Icon className="w-3.5 h-3.5 text-legal-700 flex-shrink-0" aria-hidden="true" />}
                  <span>{crumb.label}</span>
                </span>
              ) : (
                <a
                  href={crumb.href}
                  onClick={(e) => {
                    e.preventDefault();
                    if (onNavigate) onNavigate('intake');
                  }}
                  className="hover:text-legal-800 transition flex items-center gap-1 font-medium"
                  itemProp="item"
                >
                  {Icon && <Icon className="w-3.5 h-3.5 flex-shrink-0" aria-hidden="true" />}
                  <span itemProp="name">{crumb.label}</span>
                </a>
              )}
              <meta itemProp="position" content={String(idx + 1)} />
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
