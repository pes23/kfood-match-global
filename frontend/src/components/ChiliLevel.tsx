"use client";

import Image from "next/image";

export default function ChiliLevel({ level }: { level: number }) {
  const max = 3;

  // level → 빨간 고추 개수 매핑 
  const red = Math.max(0, Math.min(level - 1, max)); 
  const white = max - red;

  return (
    <div style={{ display: "flex", flexDirection: "row", gap: "4px" }}>
      {Array.from({ length: red }).map((_, i) => (
        <Image
          key={`r-${i}`}
          src="/chili-red.svg"
          width={20}
          height={20}
          alt="red chili"
        />
      ))}

      {Array.from({ length: white }).map((_, i) => (
        <Image
          key={`w-${i}`}
          src="/chili-white.svg"
          width={20}
          height={20}
          alt="white chili"
        />
      ))}
    </div>
  );
}