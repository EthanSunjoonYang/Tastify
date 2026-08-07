import { useEffect, useState } from "react";

interface SearchBarProps {
  onSearch: (ticker: string) => void;
  initialValue?: string;
}

export default function SearchBar({ onSearch, initialValue = "" }: SearchBarProps) {
  const [value, setValue] = useState(initialValue);

  useEffect(() => {
    const symbol = value.trim().toUpperCase();
    if (!symbol) return;

    const timeout = setTimeout(() => onSearch(symbol), 400);
    return () => clearTimeout(timeout);
  }, [value, onSearch]);

  return (
    <input
      type="text"
      value={value}
      onChange={(event) => setValue(event.target.value)}
      placeholder="Search a ticker (e.g. AAPL)"
      className="w-full max-w-md rounded-lg border border-slate-300 px-4 py-2 text-lg
                 shadow-sm focus:border-slate-500 focus:outline-none focus:ring-1
                 focus:ring-slate-500"
    />
  );
}
