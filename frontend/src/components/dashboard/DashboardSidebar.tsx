"use client";

import React, { useState, useEffect } from "react";
import { Sidebar, SidebarBody, SidebarLink, useSidebar } from "@/components/ui/sidebar";
import {
  Home,
  Wallet,
  Calendar,
  User,
  Activity,
  Briefcase,
  DollarSign,
  Settings,
  LogOut,
  ShieldAlert,
} from "lucide-react";
import { usePathname } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { cn } from "@/lib/utils";

// ── Sidebar Language Switcher ───────────────────────────────────────────────
// Collapsed: stacked vertically (EN on top, عربي below)
// Expanded:  side-by-side horizontally
function SidebarLanguageSwitcher() {
  const { open } = useSidebar();
  const { locale, toggleLocale } = useLanguage();
  const isArabic = locale === "ar";

  return (
    <div
      className={cn(
        "flex items-center justify-center gap-1 select-none",
        open ? "flex-row" : "flex-col"
      )}
    >
      {/* English button */}
      <button
        onClick={() => isArabic && toggleLocale()}
        className={cn(
          "relative rounded-lg font-bold text-xs tracking-wider transition-all duration-300 cursor-pointer overflow-hidden",
          open ? "px-4 py-2" : "px-3 py-1.5 w-full text-center",
          !isArabic
            ? "bg-white/10 text-white border border-white/20 shadow-[0_0_12px_rgba(121,178,83,0.15)]"
            : "text-slate-500 hover:text-slate-300 border border-transparent hover:border-white/10"
        )}
      >
        EN
        {!isArabic && (
          <motion.div
            layoutId="langIndicator"
            className="absolute bottom-0 left-1/2 -translate-x-1/2 w-3 h-[2px] rounded-full bg-[#79B253]"
            transition={{ type: "spring", stiffness: 400, damping: 25 }}
          />
        )}
      </button>

      {/* Separator */}
      <div
        className={cn(
          "bg-slate-700/50 rounded-full",
          open ? "w-px h-5" : "h-px w-5"
        )}
      />

      {/* Arabic button */}
      <button
        onClick={() => !isArabic && toggleLocale()}
        className={cn(
          "relative rounded-lg font-bold text-xs transition-all duration-300 cursor-pointer overflow-hidden",
          open ? "px-3 py-2" : "px-3 py-1.5 w-full text-center",
          isArabic
            ? "bg-white/10 text-white border border-white/20 shadow-[0_0_12px_rgba(121,178,83,0.15)]"
            : "text-slate-500 hover:text-slate-300 border border-transparent hover:border-white/10"
        )}
        style={{ fontFamily: "Cairo, system-ui, sans-serif" }}
      >
        عربي
        {isArabic && (
          <motion.div
            layoutId="langIndicator"
            className="absolute bottom-0 left-1/2 -translate-x-1/2 w-3 h-[2px] rounded-full bg-[#79B253]"
            transition={{ type: "spring", stiffness: 400, damping: 25 }}
          />
        )}
      </button>
    </div>
  );
}

// ── Main Sidebar ────────────────────────────────────────────────────────────
export function DashboardSidebar({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const pathname = usePathname();
  const { t } = useLanguage();

  useEffect(() => setMounted(true), []);

  const isNurse = pathname.includes("/nurse");

  const patientLinks = [
    {
      label: t.sidebar.patientHome,
      href: "/patient",
      icon: <Home className="text-neutral-400 dark:text-neutral-300 h-5 w-5 flex-shrink-0" />,
    },
    {
      label: t.sidebar.healthWallet,
      href: "#",
      icon: <Wallet className="text-neutral-400 dark:text-neutral-300 h-5 w-5 flex-shrink-0" />,
    },
    {
      label: t.sidebar.appointments,
      href: "#",
      icon: <Calendar className="text-neutral-400 dark:text-neutral-300 h-5 w-5 flex-shrink-0" />,
    },
    {
      label: t.sidebar.profile,
      href: "#",
      icon: <User className="text-neutral-400 dark:text-neutral-300 h-5 w-5 flex-shrink-0" />,
    },
  ];

  const nurseLinks = [
    {
      label: t.sidebar.nurseHome,
      href: "/nurse",
      icon: <Activity className="text-neutral-400 dark:text-neutral-300 h-5 w-5 flex-shrink-0" />,
    },
    {
      label: t.sidebar.activeMissions,
      href: "#",
      icon: <Briefcase className="text-neutral-400 dark:text-neutral-300 h-5 w-5 flex-shrink-0" />,
    },
    {
      label: t.sidebar.earnings,
      href: "#",
      icon: <DollarSign className="text-neutral-400 dark:text-neutral-300 h-5 w-5 flex-shrink-0" />,
    },
    {
      label: t.sidebar.settings,
      href: "#",
      icon: <Settings className="text-neutral-400 dark:text-neutral-300 h-5 w-5 flex-shrink-0" />,
    },
  ];

  const adminLinks = [
    {
      label: t.sidebar.adminHome,
      href: "/admin",
      icon: <ShieldAlert className="text-neutral-400 dark:text-neutral-300 h-5 w-5 flex-shrink-0" />,
    },
    {
      label: t.sidebar.watchtower,
      href: "/admin",
      icon: <Activity className="text-neutral-400 dark:text-neutral-300 h-5 w-5 flex-shrink-0" />,
    },
    {
      label: t.sidebar.settings,
      href: "#",
      icon: <Settings className="text-neutral-400 dark:text-neutral-300 h-5 w-5 flex-shrink-0" />,
    },
  ];

  const isAdmin = pathname.includes("/admin");
  const links = isAdmin ? adminLinks : isNurse ? nurseLinks : patientLinks;
  return (
    <div
      className={cn(
        "flex flex-col md:flex-row bg-slate-950 dark:bg-slate-950 w-full flex-1 max-w-full mx-auto overflow-hidden",
        "h-screen"
      )}
    >
      <Sidebar open={open} setOpen={setOpen}>
        <SidebarBody className="justify-between gap-10 border-r border-slate-800/60 dark:border-white/5 rtl:border-l rtl:border-r-0 bg-slate-950">
          <div className="flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
            {open ? <Logo /> : <LogoIcon />}
            <div className="mt-8 flex flex-col gap-1">
              {links.map((link, idx) => (
                <SidebarLink key={idx} link={link} />
              ))}
            </div>
          </div>

          {/* Bottom: Language switcher + Logout */}
          <div className="flex flex-col gap-4 pb-2">
            {mounted && (
              <div className="px-1">
                <SidebarLanguageSwitcher />
              </div>
            )}
            <SidebarLink
              link={{
                label: t.sidebar.logout,
                href: "/login",
                icon: (
                  <LogOut className="text-neutral-400 dark:text-neutral-300 h-5 w-5 flex-shrink-0" />
                ),
              }}
            />
          </div>
        </SidebarBody>
      </Sidebar>
      <main
        id="main-content"
        className="flex flex-1 flex-col overflow-y-auto bg-slate-950"
      >
        {children}
      </main>
    </div>
  );
}

// ── Official Wateen Logo (expanded sidebar) ─────────────────────────────────
export const Logo = () => {
  const { t } = useLanguage();
  return (
    <Link
      href="/"
      className="font-normal flex items-center gap-3 py-1 relative z-20 group select-none"
    >
      <motion.div
        whileHover={{ scale: 1.05 }}
        transition={{ type: "spring", stiffness: 400, damping: 15 }}
        className="relative shrink-0 w-9 h-9"
      >
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="/images/icon.svg"
          alt="Wateen"
          className="w-full h-full object-contain rounded-lg drop-shadow-[0_0_8px_rgba(0,136,255,0.3)]"
        />
      </motion.div>

      <motion.div
        initial={{ opacity: 0, x: -8 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -8 }}
        transition={{ duration: 0.25, ease: "easeOut" }}
      >
        <span className="font-black text-lg text-white group-hover:text-[#0088FF] transition-colors duration-300 tracking-tight">
          {t.common.wateen}
        </span>
        <div className="h-[2px] w-0 group-hover:w-full bg-gradient-to-r from-[#0088FF] to-[#8A2BE2] rounded-full transition-all duration-300" />
      </motion.div>
    </Link>
  );
};

// ── Compact icon-only logo (collapsed sidebar) ──────────────────────────────
export const LogoIcon = () => {
  return (
    <Link href="/" className="relative z-20 group select-none py-1 flex justify-center">
      <motion.div
        whileHover={{ scale: 1.1 }}
        transition={{ type: "spring", stiffness: 500, damping: 15 }}
        className="relative w-9 h-9"
      >
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="/images/icon.svg"
          alt="Wateen"
          className="w-full h-full object-contain rounded-lg drop-shadow-[0_0_6px_rgba(0,136,255,0.25)]"
        />
        {/* Ambient glow */}
        <motion.div
          className="absolute inset-0 rounded-lg"
          animate={{
            boxShadow: [
              "0 0 0px 0px rgba(0,136,255,0)",
              "0 0 10px 3px rgba(0,136,255,0.2)",
              "0 0 0px 0px rgba(0,136,255,0)",
            ],
          }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
        />
      </motion.div>
    </Link>
  );
};
