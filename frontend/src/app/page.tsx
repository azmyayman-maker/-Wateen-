import dynamic from "next/dynamic";

const LandingPage = dynamic(() => import("@/components/landing/LandingPageClient"), { ssr: false });

export default LandingPage;
