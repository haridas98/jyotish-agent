import { redirect } from "next/navigation";

export default function GuidancePage() {
  redirect("/?analysis=guidance#reports");
}
