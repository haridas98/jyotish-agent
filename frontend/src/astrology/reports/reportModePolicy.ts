import type { RelationshipUiMode } from "../relationships";

export function isVisibleInMode(visibleInModes: RelationshipUiMode[], mode: RelationshipUiMode): boolean {
  return visibleInModes.includes(mode);
}
