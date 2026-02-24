import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  basePath: "/smtr-web",
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  experimental: {
    workerThreads: false,
    cpus: 2,
  },
};

export default nextConfig;
