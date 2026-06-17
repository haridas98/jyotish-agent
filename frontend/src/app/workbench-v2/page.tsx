import { redirect } from "next/navigation";
import { debugRoutesEnabled } from "@/app/debug-route-guard";
import { WorkbenchV2Client } from "./workbench-v2-client";

export default function WorkbenchV2Page() {
  if (!debugRoutesEnabled()) {
    redirect("/charts");
  }
  return <WorkbenchV2Client />;
}
