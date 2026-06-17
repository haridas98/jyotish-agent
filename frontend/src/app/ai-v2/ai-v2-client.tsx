"use client";

import { useEffect, useState } from "react";
import { buildSingleChartEvidencePack, type AiEvidencePack } from "@/astrology";
import { calculateBirthChart, type BirthChartRequest } from "@/lib/api";
import "../workbench-v2/workbench-v2.css";

const payload: BirthChartRequest = {
  birth_date: "1998-04-30",
  birth_time: "13:45",
  gender: "male",
  place_name: "Sterlitamak, Bashkortostan, RU",
  latitude: 53.6304,
  longitude: 55.9308,
  timezone: "Asia/Yekaterinburg",
  ayanamsa: "Lahiri",
  node_type: "true",
  calculation_model: "drik_siddhanta",
  house_system: "whole_sign",
  bhava_system: "whole_sign",
  varga_scheme: "parashara",
  timezone_source: "iana",
};

export function AiV2Client() {
  const [pack, setPack] = useState<AiEvidencePack | null>(null);
  const [status, setStatus] = useState("Собираю evidence pack...");

  useEffect(() => {
    let alive = true;
    calculateBirthChart(payload)
      .then((chart) => {
        if (!alive) return;
        setPack(
          buildSingleChartEvidencePack(chart, {
            profileIds: ["haridev"],
            question: "Базовый разбор карты",
          }),
        );
        setStatus("Evidence pack готов");
      })
      .catch((error) => {
        if (!alive) return;
        setStatus(error instanceof Error ? error.message : "Не удалось собрать evidence pack");
      });
    return () => {
      alive = false;
    };
  }, []);

  return (
    <main className="workbench-v2-page">
      <div className="v2-topbar">
        <div>
          <strong>AI v2</strong>
          <span>{status}</span>
        </div>
      </div>
      <section className="v2-card v2-table-card">
        <div className="v2-card-head">
          <h2>Факторы для AI</h2>
          <small>Developer-only evidence pack table</small>
        </div>
        <div className="v2-table-scroll">
          <table>
            <thead>
              <tr>
                <th>Сущность</th>
                <th>Расчёт</th>
                <th>Важность</th>
                <th>Причина</th>
                <th>Источники</th>
              </tr>
            </thead>
            <tbody>
              {(pack?.factors ?? []).map((factor) => (
                <tr key={`${factor.entityId}-${factor.calcId}`}>
                  <td>{factor.entityId}</td>
                  <td>{factor.calcId}</td>
                  <td>{factor.relevance}</td>
                  <td>{factor.reason}</td>
                  <td>{(factor.sourceRuleIds ?? []).join(", ") || "source.pending"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
