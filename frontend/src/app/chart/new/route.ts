import { NextResponse } from "next/server";

export function GET(request: Request) {
  const forwardedHost = request.headers.get("x-forwarded-host");
  const forwardedProto = request.headers.get("x-forwarded-proto") ?? "https";
  const host = forwardedHost ?? request.headers.get("host") ?? new URL(request.url).host;

  return NextResponse.redirect(`${forwardedProto}://${host}/charts/new`);
}
