import type { ViewBlock } from "./types";

const blocks = new Map<string, ViewBlock>();

export function registerBlock(block: ViewBlock): ViewBlock {
  blocks.set(block.id, block);
  return block;
}

export function getBlock(blockId: string): ViewBlock | null {
  return blocks.get(blockId) ?? null;
}

export function listBlocks(): ViewBlock[] {
  return Array.from(blocks.values());
}
