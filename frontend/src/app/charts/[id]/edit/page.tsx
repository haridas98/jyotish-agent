"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ChartProfileForm } from "@/app/charts/chart-profile-form";
import { ProductShell } from "@/app/product-shell";
import { fetchChartProfile, type ChartProfile } from "@/lib/api";

function profileIdFromParams(value: string | string[] | undefined) {
  const raw = Array.isArray(value) ? value[0] : value;
  const parsed = Number(raw);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
}

export default function EditChartPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const profileId = profileIdFromParams(params.id);
  const [profile, setProfile] = useState<ChartProfile | null>(null);
  const [status, setStatus] = useState("Загружаю карту...");

  useEffect(() => {
    let mounted = true;
    async function loadProfile() {
      if (!profileId) {
        setStatus("Карта не найдена.");
        return;
      }
      try {
        const row = await fetchChartProfile(profileId);
        if (!mounted) return;
        setProfile(row);
        setStatus("");
      } catch (error) {
        if (!mounted) return;
        setStatus(error instanceof Error ? error.message : "Не удалось открыть карту.");
      }
    }
    void loadProfile();
    return () => {
      mounted = false;
    };
  }, [profileId]);

  return (
    <ProductShell active="charts">
      {status ? <div className="product-status">{status}</div> : null}
      {profile ? (
        <ChartProfileForm mode="edit" profile={profile} onSaved={(saved) => router.push(`/charts/${saved.id}`)} />
      ) : null}
    </ProductShell>
  );
}
