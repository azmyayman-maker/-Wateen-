import React from "react";
import { WateenSpinner } from "@/components/WateenSpinner";

export default function Loading() {
  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/40 backdrop-blur-md transition-all duration-300">
      <div className="flex flex-col items-center justify-center gap-8">
        <WateenSpinner />
      </div>
    </div>
  );
}
