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
  // Next.js Docker Standalone mode
  output: 'standalone',
};

export default nextConfig;
