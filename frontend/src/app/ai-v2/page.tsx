import { redirect } from "next/navigation";
import { debugRoutesEnabled } from "@/app/debug-route-guard";
import { AiV2Client } from "./ai-v2-client";

export default function AiV2Page() {
  if (!debugRoutesEnabled()) {
    redirect("/charts");
  }
  return <AiV2Client />;
}
