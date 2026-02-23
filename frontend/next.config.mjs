/** @type {import('next').NextConfig} */
const nextConfig = {
  // Disable automatic OpenTelemetry tracing which crashes with 
  // TypeError: Cannot read properties of undefined (reading 'clientModules')
  experimental: {
    instrumentationHook: false,
    optimizePackageImports: ['lucide-react', 'framer-motion', '@react-three/fiber'],
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'i.pravatar.cc',
      },
      {
        protocol: 'https',
        hostname: 'ui-avatars.com',
      }
    ]
  },
  webpack: (config, { isServer }) => {
    // Attempt to bypass Next.js internal client module tracking bug 
    // where some dynamically imported or heavy client components cause CSS entry tracking to fail
    if (isServer) {
        config.externals = [...(config.externals || []), 'canvas', 'jsdom'];
    }
    return config;
  },
};

export default nextConfig;
