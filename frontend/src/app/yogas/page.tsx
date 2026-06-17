import { redirect } from "next/navigation";

export default function YogasPage() {
  redirect("/?analysis=yogas#reports");
}
