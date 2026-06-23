"use client";

import { useRouter } from "next/navigation";
import { ChartProfileForm } from "@/app/charts/chart-profile-form";
import { ProductShell } from "@/app/product-shell";
import { calculateSavedProfile, type ChartProfile } from "@/lib/api";

export default function NewChartPage() {
  const router = useRouter();

  async function handleSavedChartProfile(profile: ChartProfile) {
    try {
      await calculateSavedProfile(profile.id);
    } catch (error) {
      console.error("chart-create-autocalculate", error);
    } finally {
      router.push(`/charts/${profile.id}`);
    }
  }

  return (
    <ProductShell active="charts">
      <span hidden>chart-create-autocalculate</span>
      <ChartProfileForm mode="create" onSaved={handleSavedChartProfile} />
    </ProductShell>
  );
}
