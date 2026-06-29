import React from "react";
import { Sparkles, Loader2, Check } from "lucide-react";

interface VibeInputProps {
  prompt: string;
  setPrompt: (val: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  loading: boolean;
  onSuggestionClick: (suggestion: string) => void;
}

export default function VibeInput({
  prompt,
  setPrompt,
  onSubmit,
  loading,
  onSuggestionClick
}: VibeInputProps) {
  // 3 suggestions with corresponding premium theme colors
  const suggestions = [
    {
      text: "Feeling low, need something that lifts me slowly",
      colorClass: "text-amber-400 border-amber-500/35 hover:border-amber-400 hover:bg-amber-500/10 hover:shadow-amber-500/5",
    },
    {
      text: "Melancholy but hopeful",
      colorClass: "text-indigo-400 border-indigo-500/35 hover:border-indigo-400 hover:bg-indigo-500/10 hover:shadow-indigo-500/5",
    },
    {
      text: "Angry but want to calm down",
      colorClass: "text-rose-400 border-rose-500/35 hover:border-rose-400 hover:bg-rose-500/10 hover:shadow-rose-500/5",
    }
  ];

  return (
    <div className="flex flex-col gap-1.5 select-none font-sans min-w-0 justify-center w-full md:w-auto">
      {/* Vibe Checker Input Form */}
      <form onSubmit={onSubmit} className="flex items-center gap-2 flex-shrink-0 w-full md:w-auto">
        <div className="relative flex items-center bg-zinc-900 border border-zinc-700/60 hover:border-emerald-500/40 focus-within:border-emerald-500 hover:scale-[1.01] focus-within:ring-2 focus-within:ring-emerald-500/20 rounded-full py-1.5 px-3.5 transition-all duration-300 w-full md:w-72 shadow-md shadow-black/20 flex-1 md:flex-initial">
          <Sparkles className="w-3.5 h-3.5 text-emerald-400 mr-1.5 flex-shrink-0 animate-pulse" />
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value.slice(0, 500))}
            placeholder="What is your vibe today?"
            disabled={loading}
            className="bg-transparent border-none outline-none text-white placeholder-zinc-500 text-[11px] w-full font-medium"
          />
          {prompt.length > 0 && (
            <span className="text-zinc-500 text-[9px] ml-1 flex-shrink-0">
              {prompt.length}/500
            </span>
          )}
        </div>

        {/* Dynamic Build Queue Button */}
        {prompt.trim().length > 0 && (
          <button
            type="submit"
            disabled={loading}
            className="bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-400 hover:to-teal-300 text-black font-black text-[11px] uppercase tracking-wider px-4 py-2 rounded-full transition-all duration-300 transform active:scale-95 hover:scale-[1.03] flex items-center gap-1.5 cursor-pointer shadow-md shadow-emerald-500/20 hover:shadow-lg hover:shadow-emerald-400/30 border border-emerald-300/20 flex-shrink-0"
          >
            {loading ? (
              <>
                <Loader2 className="w-3 h-3 animate-spin" />
                <span>Building...</span>
              </>
            ) : (
              <>
                <Check className="w-3.5 h-3.5 stroke-[3]" />
                <span>Build My Queue</span>
              </>
            )}
          </button>
        )}
      </form>

      {/* Suggestion Prompts Aligned Below Input (Screen 1) */}
      <div className="hidden md:flex items-center gap-1.5 flex-wrap">
        <span className="text-zinc-500 text-[8px] font-bold uppercase tracking-wider mr-0.5 whitespace-nowrap">
          Suggestions:
        </span>
        {suggestions.map((sug, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => onSuggestionClick(sug.text)}
            className={`bg-zinc-950 border text-[8px] px-2 py-0.5 rounded-full font-bold transition-all duration-300 hover:-translate-y-0.5 active:translate-y-0 cursor-pointer shadow-sm ${sug.colorClass}`}
          >
            {sug.text}
          </button>
        ))}
      </div>
    </div>
  );
}
