/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['@paper-design/shaders-react'],
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
  }
};

export default nextConfig;
