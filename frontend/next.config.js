/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3002/api',
  },
  
  // Proxy API calls to backend server (avoids CORS and mixed-content issues)
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL || 'http://16.171.111.4:3002';
    
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
}

module.exports = nextConfig

