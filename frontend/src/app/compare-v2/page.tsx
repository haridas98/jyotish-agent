import { relationshipRecipes } from "@/astrology";
import "../workbench-v2/workbench-v2.css";

export default function CompareV2Page() {
  const recipes = Object.values(relationshipRecipes);

  return (
    <main className="workbench-v2-page">
      <div className="v2-topbar">
        <div>
          <strong>Compare v2</strong>
          <span>Рецепты отношений без повторных блоков</span>
        </div>
      </div>
      <section className="v2-card v2-table-card">
        <div className="v2-card-head">
          <h2>Роли</h2>
          <small>Каждая роль задаёт нужные дома, D-карты и AI-факторы</small>
        </div>
        <div className="v2-table-scroll">
          <table>
            <thead>
              <tr>
                <th>Роль</th>
                <th>D-карты</th>
                <th>Главные факторы A</th>
                <th>Главные факторы B</th>
                <th>Общие проверки</th>
              </tr>
            </thead>
            <tbody>
              {recipes.map((recipe) => (
                <tr key={recipe.id}>
                  <td>{recipe.label}</td>
                  <td>{recipe.requiredVargas.join(", ")}</td>
                  <td>{recipe.profileAFactors.map((factor) => factor.entityId).join(", ") || "—"}</td>
                  <td>{recipe.profileBFactors.map((factor) => factor.entityId).join(", ") || "—"}</td>
                  <td>{recipe.sharedFactors.map((factor) => factor.entityId).join(", ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
