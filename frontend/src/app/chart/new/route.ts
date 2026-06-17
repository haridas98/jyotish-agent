import { NextResponse } from "next/server";

const PUBLIC_ORIGIN = "https://jyotish-agent.duckdns.org";

function isInternalHost(host: string): boolean {
  return (
    host.startsWith("0.0.0.0") ||
    host.startsWith("127.") ||
    host.startsWith("10.") ||
    host.startsWith("172.") ||
    host.startsWith("192.168.") ||
    /^\d{1,3}(\.\d{1,3}){3}(:\d+)?$/.test(host)
  );
}

export function GET(request: Request) {
  const forwardedHost = request.headers.get("x-forwarded-host");
  const forwardedProto = request.headers.get("x-forwarded-proto") ?? "https";
  const host = forwardedHost ?? request.headers.get("host") ?? new URL(request.url).host;
  const origin = forwardedHost && isInternalHost(host) ? PUBLIC_ORIGIN : `${forwardedProto}://${host}`;

  return NextResponse.redirect(`${origin}/charts/new`);
}
