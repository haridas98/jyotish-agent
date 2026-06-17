import { redirect } from "next/navigation";

export default function LegacyNewChartPage() {
  redirect("/charts/new");
}
