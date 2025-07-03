import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  async rewrites() {
    return [
      // Auth rewrite - maps /api/auth/* to backend /auth/* (must come before general /api/ rule)
      {
        source: '/api/auth/:path*',
        destination: 'http://127.0.0.1:8000/auth/:path*',
      },
      // API rewrite - maps /api/* to backend /api/*
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/api/:path*',
      },
      // WebSocket rewrite (note: this won't work for WebSockets, just here for reference)
      {
        source: '/ws/:path*',
        destination: 'http://127.0.0.1:8000/ws/:path*',
      },
    ];
  },
};

export default nextConfig;
