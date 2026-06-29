import React, { useState } from "react";
import { Plus, Check, Play, Info, Sparkles, Smile, ArrowRight, Activity, Cpu, Star } from "lucide-react";
import { VibeQueue, Track } from "@/lib/types";
import TrackCard from "./TrackCard";

interface QueueResultsProps {
  queue: VibeQueue;
  onSave: (name: string) => Promise<void>;
  user: any;
  playingTrackId: string | null;
  isPlaying: boolean;
  onPlayToggle: (track: Track) => void;
}

export default function QueueResults({ 
  queue, 
  onSave, 
  user,
  playingTrackId,
  isPlaying,
  onPlayToggle
}: QueueResultsProps) {
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const { prompt, emotion_type, emotional_profile, tracks, confidence, ai_explanation, generated_at } = queue;

  // Split tracks
  const nowTracks = tracks.slice(0, 4);
  const nextTracks = tracks.slice(4, 8);
  const soonTracks = tracks.slice(8, 12);

  // Confidence color utility
  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return "text-emerald-500 bg-emerald-500/10 border-emerald-500/20";
    if (score >= 0.5) return "text-amber-500 bg-amber-500/10 border-amber-500/20";
    return "text-rose-500 bg-rose-500/10 border-rose-500/20";
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const defaultName = `${prompt.slice(0, 20)} Vibe`;
      await onSave(defaultName);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (e) {
      console.error("Failed to save playlist", e);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 text-zinc-100 font-sans pb-16 select-none max-w-5xl mx-auto w-full px-2">
      {/* Header Panel */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-zinc-800 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <Star className="w-5 h-5 text-amber-400 fill-amber-400/85 animate-pulse" />
            <span className="text-lg font-extrabold tracking-wide bg-gradient-to-r from-emerald-400 via-cyan-400 to-indigo-400 text-transparent bg-clip-text drop-shadow-[0_0_15px_rgba(16,185,129,0.15)]">
              Your Vibe Queue
            </span>
          </div>
          <h2 className="text-3xl font-extrabold text-white mt-1 capitalize">"{prompt}"</h2>
          <div className="flex items-center gap-3 text-zinc-400 text-xs mt-2 font-medium">
            <span>{tracks.length} Songs</span>
            <span>•</span>
            <span>~42 mins</span>
            <span>•</span>
            <span className="bg-zinc-800 text-zinc-300 px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider">
              {emotion_type.replace(/_/g, " ")}
            </span>
          </div>
        </div>

        {/* Save Playlist Button */}
        <button
          onClick={handleSave}
          disabled={saving || !user}
          className={`flex items-center gap-2 font-bold text-sm px-6 py-3 rounded-full transition duration-300 transform active:scale-95 cursor-pointer shadow-lg ${
            !user 
              ? "bg-zinc-800 text-zinc-500 border border-zinc-700/50 cursor-not-allowed"
              : saved
                ? "bg-emerald-500 text-black shadow-emerald-500/10"
                : "bg-white text-black hover:bg-zinc-200"
          }`}
          title={!user ? "Sign in to save this playlist to your profile" : "Save to library"}
        >
          {saved ? (
            <>
              <Check className="w-4 h-4" />
              <span>Saved!</span>
            </>
          ) : (
            <>
              <Plus className="w-4 h-4" />
              <span>{!user ? "Sign in to Save" : "Save Playlist"}</span>
            </>
          )}
        </button>
      </div>

      {/* Grid: AI Explanation and Emotional Profile Transparency */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        {/* AI Explanation Box (Left 3 columns) */}
        <div className="md:col-span-3 bg-zinc-900/60 rounded-xl p-5 border border-zinc-800/80 flex flex-col gap-3 backdrop-blur relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/5 rounded-full blur-3xl -mr-8 -mt-8" />
          <div className="flex items-center gap-2 text-emerald-400 text-sm font-semibold">
            <Sparkles className="w-4 h-4" />
            <span>AI Recommendation Insight</span>
          </div>
          <p className="text-zinc-300 text-sm leading-relaxed font-medium">
            {ai_explanation || "These tracks were selected to match the emotional tones, energy shifts, and acoustic profile of your vibe prompt."}
          </p>
        </div>

        {/* Emotional Profile Card (Right 2 columns) */}
        <div className="md:col-span-2 bg-zinc-900/60 rounded-xl p-5 border border-zinc-800/80 flex flex-col gap-4 backdrop-blur">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-zinc-400 text-sm font-semibold">
              <Cpu className="w-4 h-4 text-zinc-500" />
              <span>Pipeline Analysis</span>
            </div>
            
            {/* Confidence score */}
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${getConfidenceColor(confidence)}`}>
              {Math.round(confidence * 100)}% Confidence
            </span>
          </div>

          {/* Visualizing Emotional Arc Transition */}
          <div className="flex flex-col gap-3">
            {/* Current Vibe */}
            <div className="flex justify-between items-center text-xs">
              <span className="text-zinc-500 font-semibold uppercase tracking-wider">Current State</span>
              <span className="text-white font-bold capitalize">{emotional_profile.current.primary_emotion}</span>
            </div>
            <div className="grid grid-cols-2 gap-3 bg-zinc-950/40 p-2.5 rounded border border-zinc-800/50">
              <div className="flex flex-col gap-1.5">
                <span className="text-[10px] text-zinc-500 uppercase font-semibold">Valence (Mood)</span>
                <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                  <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${emotional_profile.current.valence * 100}%` }} />
                </div>
              </div>
              <div className="flex flex-col gap-1.5">
                <span className="text-[10px] text-zinc-500 uppercase font-semibold">Energy</span>
                <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${emotional_profile.current.energy * 100}%` }} />
                </div>
              </div>
            </div>

            {/* Transition Arc Indicator */}
            {emotional_profile.desired && (
              <>
                <div className="flex items-center justify-center py-0.5">
                  <div className="flex items-center gap-1.5 text-zinc-500 text-[10px] font-bold uppercase tracking-wider bg-zinc-800 px-3 py-1 rounded-full border border-zinc-700/30">
                    <span>Transition</span>
                    <ArrowRight className="w-3 h-3 text-emerald-400" />
                    <span className="text-emerald-400">{emotional_profile.transition}</span>
                  </div>
                </div>

                {/* Desired Vibe */}
                <div className="flex justify-between items-center text-xs">
                  <span className="text-zinc-500 font-semibold uppercase tracking-wider">Desired State</span>
                  <span className="text-white font-bold capitalize">{emotional_profile.desired.primary_emotion}</span>
                </div>
                <div className="grid grid-cols-2 gap-3 bg-zinc-950/40 p-2.5 rounded border border-zinc-800/50">
                  <div className="flex flex-col gap-1.5">
                    <span className="text-[10px] text-zinc-500 uppercase font-semibold">Valence (Mood)</span>
                    <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-400 rounded-full" style={{ width: `${emotional_profile.desired.valence * 100}%` }} />
                    </div>
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <span className="text-[10px] text-zinc-500 uppercase font-semibold">Energy</span>
                    <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                      <div className="h-full bg-indigo-400 rounded-full" style={{ width: `${emotional_profile.desired.energy * 100}%` }} />
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Playlist Grid Column Headers */}
      <div className="flex flex-col gap-8 mt-4 bg-zinc-900/30 p-2 md:p-4 rounded-xl border border-zinc-850">
        {/* Playlist Table Head */}
        <div className="grid grid-cols-[16px_1fr_60px] md:grid-cols-[16px_4fr_3fr_3fr_80px] gap-2.5 md:gap-4 px-2 md:px-4 text-xs font-bold text-zinc-500 uppercase border-b border-zinc-800 pb-3 select-none">
          <div className="text-center">#</div>
          <div>Title</div>
          <div className="hidden md:block">Album</div>
          <div className="hidden md:block">Vibe Alignment</div>
          <div className="text-right">Duration</div>
        </div>

        {/* Section: NOW (Tracks 1-4) */}
        {nowTracks.length > 0 && (
          <div className="flex flex-col gap-1">
            <h3 className="text-sm font-bold text-emerald-400 uppercase tracking-widest px-4 mb-2 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
              <span>Now</span>
            </h3>
            {nowTracks.map((t, idx) => (
              <TrackCard 
                key={t.track.id} 
                trackItem={t} 
                index={idx + 1} 
                isPlaying={playingTrackId === t.track.id && isPlaying}
                onPlayToggle={() => onPlayToggle(t.track)}
              />
            ))}
          </div>
        )}

        {/* Section: NEXT (Tracks 5-8) */}
        {nextTracks.length > 0 && (
          <div className="flex flex-col gap-1">
            <h3 className="text-sm font-bold text-indigo-400 uppercase tracking-widest px-4 mb-2">
              Next
            </h3>
            {nextTracks.map((t, idx) => (
              <TrackCard 
                key={t.track.id} 
                trackItem={t} 
                index={idx + 5} 
                isPlaying={playingTrackId === t.track.id && isPlaying}
                onPlayToggle={() => onPlayToggle(t.track)}
              />
            ))}
          </div>
        )}

        {/* Section: SOON (Tracks 9-12) */}
        {soonTracks.length > 0 && (
          <div className="flex flex-col gap-1">
            <h3 className="text-sm font-bold text-zinc-500 uppercase tracking-widest px-4 mb-2">
              Soon
            </h3>
            {soonTracks.map((t, idx) => (
              <TrackCard 
                key={t.track.id} 
                trackItem={t} 
                index={idx + 9} 
                isPlaying={playingTrackId === t.track.id && isPlaying}
                onPlayToggle={() => onPlayToggle(t.track)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
