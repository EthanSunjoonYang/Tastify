import { useState } from "react";

import About from "./pages/About";
import Dashboard from "./pages/Dashboard";

type Tab = "dashboard" | "about";

export default function App() {
  const [tab, setTab] = useState<Tab>("dashboard");

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-5xl gap-6 px-4 py-3">
          <button
            onClick={() => setTab("dashboard")}
            className={`text-sm font-medium ${
              tab === "dashboard" ? "text-slate-900" : "text-slate-400"
            }`}
          >
            Dashboard
          </button>
          <button
            onClick={() => setTab("about")}
            className={`text-sm font-medium ${
              tab === "about" ? "text-slate-900" : "text-slate-400"
            }`}
          >
            Methodology
          </button>
        </div>
      </nav>

      {tab === "dashboard" ? <Dashboard /> : <About />}
    </div>
  );
}
