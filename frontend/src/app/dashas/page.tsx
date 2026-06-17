import { redirect } from "next/navigation";

export default function DashasPage() {
  redirect("/?analysis=timeline#reports");
}
