import React, { useState } from "react";
import { Play, Pause, Activity, Flame, Radio, Heart, ExternalLink } from "lucide-react";
import { RankedTrack } from "@/lib/types";

interface TrackCardProps {
  trackItem: RankedTrack;
  index: number;
  isPlaying?: boolean;
  onPlayToggle?: () => void;
}

export default function TrackCard({ 
  trackItem, 
  index, 
  isPlaying = false, 
  onPlayToggle 
}: TrackCardProps) {
  const [hovered, setHovered] = useState(false);
  const { track, similarity_score, alignment_score, arc_score, composite_score } = trackItem;

  // Format ms to MM:SS
  const formatDuration = (ms: number) => {
    const minutes = Math.floor(ms / 60000);
    const seconds = ((ms % 60000) / 1000).toFixed(0);
    return `${minutes}:${Number(seconds) < 10 ? "0" : ""}${seconds}`;
  };

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className="grid grid-cols-[16px_1fr_60px] md:grid-cols-[16px_4fr_3fr_3fr_80px] items-center gap-2.5 md:gap-4 py-2 px-2 md:py-2.5 md:px-4 hover:bg-zinc-800/60 rounded-md transition duration-150 select-none group border-b border-zinc-900/30"
    >
      {/* Index or Play icon */}
      <div className="flex items-center justify-center text-xs md:text-sm font-semibold text-zinc-500 w-4 h-4">
        {hovered ? (
          <button 
            onClick={() => onPlayToggle && onPlayToggle()}
            className="text-white hover:scale-105 active:scale-95 transition"
          >
            {isPlaying ? (
              <Pause className="w-4 h-4 fill-white" />
            ) : (
              <Play className="w-4 h-4 fill-white" />
            )}
          </button>
        ) : isPlaying ? (
          <Activity className="w-4 h-4 text-emerald-500 animate-pulse" />
        ) : (
          <span>{index}</span>
        )}
      </div>

      {/* Title & Artist */}
      <div className="flex items-center gap-2 md:gap-3 min-w-0">
        <div className="w-8 h-8 md:w-10 md:h-10 bg-zinc-800 rounded flex-shrink-0 flex items-center justify-center font-bold text-[10px] md:text-xs text-zinc-400 border border-zinc-700/30 overflow-hidden relative">
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-indigo-500/10 opacity-50" />
          {track.track_name.slice(0, 2).toUpperCase()}
        </div>
        <div className="flex flex-col min-w-0">
          <span className="text-white font-medium text-xs md:text-sm truncate group-hover:text-emerald-400 transition">
            {track.track_name}
          </span>
          <span className="text-zinc-450 text-[10px] md:text-xs truncate mt-0.5">
            {track.artist}
          </span>
        </div>
      </div>

      {/* Album */}
      <div className="hidden md:block text-zinc-400 text-sm truncate min-w-0">
        {track.album}
      </div>

      {/* Emotional Metrics (Valence, Energy, Similarity, Arc) */}
      <div className="hidden md:flex items-center gap-4 text-xs font-mono text-zinc-500">
        <div className="flex items-center gap-1 hover:text-white transition cursor-help" title="Acoustic Alignment Score">
          <Flame className="w-3.5 h-3.5 text-emerald-500/70" />
          <span>{Math.round(alignment_score * 100)}%</span>
        </div>
        <div className="flex items-center gap-1 hover:text-white transition cursor-help" title="Positional Emotional Arc Score">
          <Radio className="w-3.5 h-3.5 text-indigo-400/70" />
          <span>{Math.round(arc_score * 100)}%</span>
        </div>
        <div className="text-[10px] bg-zinc-800 text-zinc-400 px-2 py-0.5 rounded border border-zinc-700/20 capitalize font-sans">
          {track.track_genre}
        </div>
      </div>

      {/* Duration */}
      <div className="text-zinc-400 text-xs md:text-sm text-right font-medium flex items-center justify-end gap-1.5 md:gap-3 pr-1 md:pr-2">
        {hovered && (
          <div className="hidden md:flex items-center gap-2">
            <a 
              href={`https://open.spotify.com/track/${track.id}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-zinc-500 hover:text-emerald-400 transition duration-150"
              title="Open in Spotify"
            >
              <ExternalLink className="w-4 h-4" />
            </a>
            <button className="text-zinc-500 hover:text-emerald-400 transition duration-150">
              <Heart className="w-4 h-4" />
            </button>
          </div>
        )}
        <span>{formatDuration(track.duration_ms)}</span>
      </div>
    </div>
  );
}
