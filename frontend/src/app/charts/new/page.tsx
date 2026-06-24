"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ChartProfileForm } from "@/app/charts/chart-profile-form";
import { ProductShell } from "@/app/product-shell";
import { calculateSavedProfile, type ChartProfile } from "@/lib/api";

export default function NewChartPage() {
  const router = useRouter();
  const [workflowStatus, setWorkflowStatus] = useState("");

  async function handleSavedChartProfile(profile: ChartProfile) {
    setWorkflowStatus("Расчет запрошен...");
    try {
      await calculateSavedProfile(profile.id);
      setWorkflowStatus("Расчет завершен.");
    } catch (error) {
      setWorkflowStatus(error instanceof Error ? error.message : "Не удалось рассчитать сохраненную карту.");
    } finally {
      router.push(`/charts/${profile.id}`);
    }
  }

  return (
    <ProductShell active="charts">
      <span hidden>chart-create-autocalculate</span>
      <span hidden>chart-workflow-state-calculation-requested</span>
      {workflowStatus ? <div className="product-status">{workflowStatus}</div> : null}
      <ChartProfileForm mode="create" onSaved={handleSavedChartProfile} />
    </ProductShell>
  );
}
