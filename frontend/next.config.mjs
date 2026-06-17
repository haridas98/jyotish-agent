const apiProxyTarget =
  process.env.NEXT_API_PROXY_TARGET ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  "http://127.0.0.1:8100";
const debugRoutesEnabled =
  process.env.ENABLE_DEBUG_ROUTES === "true" ||
  process.env.NEXT_PUBLIC_ENABLE_DEBUG_ROUTES === "true" ||
  process.env.NODE_ENV !== "production";

/** @type {import('next').NextConfig} */
const nextConfig = {
  async redirects() {
    if (debugRoutesEnabled) {
      return [];
    }
    return ["/workbench-v2", "/ai-v2", "/compare-v2"].map((source) => ({
      source,
      destination: "/charts",
      permanent: false,
    }));
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${apiProxyTarget}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
