import type { CalculationId, CalculationModule } from "./types";

const calculationModules = new Map<CalculationId, CalculationModule>();

export function registerCalculation<TOutput>(module: CalculationModule<TOutput>): CalculationModule<TOutput> {
  calculationModules.set(module.id, module as CalculationModule);
  return module;
}

export function getCalculationModule(id: CalculationId): CalculationModule {
  const module = calculationModules.get(id);
  if (!module) {
    throw new Error(`Unknown calculation module: ${id}`);
  }
  return module;
}

export function listCalculationModules(): CalculationModule[] {
  return Array.from(calculationModules.values());
}

export function hasCalculationModule(id: CalculationId): boolean {
  return calculationModules.has(id);
}
