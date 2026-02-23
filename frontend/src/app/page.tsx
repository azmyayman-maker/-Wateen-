import dynamic from "next/dynamic";

const LandingPage = dynamic(() => import("./(public)/page"), { ssr: false });

export default LandingPage;
