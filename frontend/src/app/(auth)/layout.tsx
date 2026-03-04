"use client";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative min-h-screen w-full overflow-hidden select-none">
      {/* ─── THE CINEMATIC CANVAS: Full-Bleed Video Background ─── */}
      <video
        autoPlay
        loop
        muted
        playsInline
        className="absolute inset-0 w-full h-full object-cover z-0"
      >
        <source src="/videos/medical-bg.mp4?v=1" type="video/mp4" />
      </video>

      {/* ─── BRAND GRADIENT OVERLAY ─── */}
      {/* Layer 1: Heavy directional gradient for brand identity + readability */}
      <div
        className="absolute inset-0 z-[1] bg-gradient-to-br from-slate-950/90 via-slate-900/80 to-cyan-900/70"
        style={{ mixBlendMode: "multiply" }}
        aria-hidden="true"
      />
      {/* Layer 2: Subtle blur veil for cinematic depth */}
      <div
        className="absolute inset-0 z-[2] backdrop-blur-[2px]"
        aria-hidden="true"
      />

      {/* ─── AMBIENT PARTICLES (decorative) ─── */}
      <div className="absolute inset-0 z-[3] overflow-hidden pointer-events-none" aria-hidden="true">
        {/* Floating orb — top left */}
        <div className="absolute -top-20 -left-20 w-72 h-72 rounded-full bg-cyan-500/10 blur-3xl animate-pulse" />
        {/* Floating orb — bottom right */}
        <div
          className="absolute -bottom-32 -right-32 w-96 h-96 rounded-full bg-purple-500/8 blur-3xl"
          style={{ animation: "pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite 1.5s" }}
        />
        {/* Floating orb — center accent */}
        <div
          className="absolute top-1/2 left-1/3 w-48 h-48 rounded-full bg-teal-400/5 blur-2xl"
          style={{ animation: "pulse 6s cubic-bezier(0.4, 0, 0.6, 1) infinite 3s" }}
        />
      </div>

      {/* ─── CONTENT LAYER ─── */}
      <main
        id="main-content"
        className="relative z-10 min-h-screen flex items-center justify-center p-4 sm:p-6"
      >
        {children}
      </main>
    </div>
  );
}
