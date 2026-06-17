export function debugRoutesEnabled(): boolean {
  return (
    process.env.ENABLE_DEBUG_ROUTES === "true" ||
    process.env.NEXT_PUBLIC_ENABLE_DEBUG_ROUTES === "true" ||
    process.env.NODE_ENV !== "production"
  );
}
