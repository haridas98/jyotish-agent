"use client";

import { useRouter } from "next/navigation";
import { ChartProfileForm } from "@/app/charts/chart-profile-form";
import { ProductShell } from "@/app/product-shell";

export default function NewChartPage() {
  const router = useRouter();

  return (
    <ProductShell active="charts">
      <ChartProfileForm mode="create" onSaved={(profile) => router.push(`/charts/${profile.id}`)} />
    </ProductShell>
  );
}
