import { relationshipRecipes } from "@/astrology";
import { debugRoutesEnabled } from "@/app/debug-route-guard";
import { redirect } from "next/navigation";
import "../workbench-v2/workbench-v2.css";

export default function CompareV2Page() {
  if (!debugRoutesEnabled()) {
    redirect("/charts");
  }

  const recipes = Object.values(relationshipRecipes);

  return (
    <main className="workbench-v2-page">
      <div className="v2-topbar">
        <div>
          <strong>Compare v2</strong>
          <span>Relationship recipe registry preview</span>
        </div>
      </div>
      <section className="v2-card v2-table-card">
        <div className="v2-card-head">
          <h2>Recipes</h2>
          <small>Typed roles, factors and directed focus layers.</small>
        </div>
        <div className="v2-table-scroll">
          <table>
            <thead>
              <tr>
                <th>Recipe</th>
                <th>Status</th>
                <th>A to B</th>
                <th>B to A</th>
                <th>Mutual factors</th>
              </tr>
            </thead>
            <tbody>
              {recipes.map((recipe) => (
                <tr key={recipe.id}>
                  <td>{recipe.label.ru}</td>
                  <td>{recipe.status}</td>
                  <td>{recipe.perspectiveAtoB.primaryEntityIds.join(", ") || "-"}</td>
                  <td>{recipe.perspectiveBtoA.primaryEntityIds.join(", ") || "-"}</td>
                  <td>{recipe.mutualFocus.relationshipFactorIds.join(", ") || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
