"use client";

import { useEffect, useId, useRef } from "react";

export type InterfaceMode = "pro" | "beginner";

type InterfaceModeSwitchProps = {
  value: InterfaceMode;
  onChange: (value: InterfaceMode) => void;
};

export const INTERFACE_MODE_STORAGE_KEY = "jyotish-interface-mode";

export function InterfaceModeSwitch({ value, onChange }: InterfaceModeSwitchProps) {
  const rootRef = useRef<HTMLDivElement | null>(null);
  const groupId = useId();

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;

    function handleNativeEvent(event: Event) {
      const target = event.target instanceof Element ? event.target.closest<HTMLElement>("[data-interface-mode]") : null;
      const mode = target?.dataset.interfaceMode;
      if (mode === "pro" || mode === "beginner") {
        onChange(mode);
      }
    }

    root.addEventListener("pointerdown", handleNativeEvent);
    root.addEventListener("click", handleNativeEvent);
    return () => {
      root.removeEventListener("pointerdown", handleNativeEvent);
      root.removeEventListener("click", handleNativeEvent);
    };
  }, [onChange]);

  return (
    <div ref={rootRef} className="product-mode-switch" aria-label="Режим интерфейса" role="radiogroup">
      <label className={value === "beginner" ? "active" : ""}>
        <input
          type="radio"
          name={`${groupId}-interface-mode`}
          value="beginner"
          data-interface-mode="beginner"
          data-interface-mode-input="beginner"
          checked={value === "beginner"}
          onChange={() => onChange("beginner")}
        />
        <span>Новичок</span>
      </label>
      <label className={value === "pro" ? "active" : ""}>
        <input
          type="radio"
          name={`${groupId}-interface-mode`}
          value="pro"
          data-interface-mode="pro"
          data-interface-mode-input="pro"
          checked={value === "pro"}
          onChange={() => onChange("pro")}
        />
        <span>Астролог</span>
      </label>
    </div>
  );
}
