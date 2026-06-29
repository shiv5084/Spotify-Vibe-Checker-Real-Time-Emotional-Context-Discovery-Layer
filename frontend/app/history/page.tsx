"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { supabase } from "@/lib/supabase";
import { UserProfile, VibeQueue } from "@/lib/types";
import Sidebar from "@/components/Sidebar";
import TrackCard from "@/components/TrackCard";
import { 
  ArrowLeft, Clock, Calendar, ShieldAlert, ChevronDown, ChevronUp, 
  Trash2, Smile, Activity, Music, LogOut, ArrowRight, Cpu, Sparkles 
} from "lucide-react";

export default function HistoryPage() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [historyItems, setHistoryItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedItemId, setExpandedItemId] = useState<string | null>(null);

  // Saved playlists local state for sidebar
  const [savedPlaylists, setSavedPlaylists] = useState<any[]>([]);

  // Load user auth session and auth listeners on mount
  useEffect(() => {
    // Clean up URL hash if it contains access_token from Supabase redirection
    if (typeof window !== "undefined" && window.location.hash.includes("access_token=")) {
      window.history.replaceState(null, "", window.location.pathname + window.location.search);
    }

    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user) {
        const profile: UserProfile = {
          id: session.user.id,
          email: session.user.email || "",
          display_name: session.user.user_metadata.full_name || session.user.user_metadata.name || "Vibe User",
          avatar_url: session.user.user_metadata.avatar_url || null
        };
        setUser(profile);
        fetchHistory(profile.id);
      } else {
        setLoading(false);
      }
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session?.user) {
        const profile: UserProfile = {
          id: session.user.id,
          email: session.user.email || "",
          display_name: session.user.user_metadata.full_name || session.user.user_metadata.name || "Vibe User",
          avatar_url: session.user.user_metadata.avatar_url || null
        };
        setUser(profile);
        fetchHistory(profile.id);
      } else {
        setUser(null);
        setHistoryItems([]);
        setLoading(false);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  // Load saved playlists when user logs in or out
  useEffect(() => {
    if (user) {
      const saved = localStorage.getItem(`vibe_checker_saved_playlists_${user.id}`);
      if (saved) {
        try {
          setSavedPlaylists(JSON.parse(saved));
        } catch (e) {
          console.error(e);
          setSavedPlaylists([]);
        }
      } else {
        setSavedPlaylists([]);
      }
    } else {
      setSavedPlaylists([]);
    }
  }, [user]);

  const fetchHistory = async (userId: string) => {
    setLoading(true);
    try {
      const { data, error } = await supabase
        .from("prompt_history")
        .select("*")
        .eq("user_id", userId)
        .order("created_at", { ascending: false });

      if (error) throw error;
      setHistoryItems(data || []);
    } catch (e) {
      console.error("Failed to load prompt history", e);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async () => {
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: typeof window !== "undefined" ? window.location.origin + "/history" : "",
        }
      });
      if (error) throw error;
    } catch (err: any) {
      console.error("Sign-in failed", err.message);
      // Fallback demo user
      const mockUser = {
        id: "mock-user-12345",
        email: "demo@vibechecker.com",
        display_name: "Demo Vibe User",
        avatar_url: null
      };
      setUser(mockUser);
      // Fetch mock local data if offline
      setHistoryItems([
        {
          id: "1",
          prompt_text: "Melancholy but hopeful mood",
          created_at: new Date().toISOString(),
          confidence: 0.95,
          latency_ms: 1200,
          emotional_profile: {
            emotion_type: "mixed_emotion",
            transition: "gradual",
            current: { primary_emotion: "sad", valence: 0.2, energy: 0.3 },
            desired: { primary_emotion: "hopeful", valence: 0.7, energy: 0.6 }
          },
          queue_result: {
            ai_explanation: "These tracks were selected to transition from a sad mood to a more hopeful tone.",
            tracks: [
              {
                track: { id: "song1", track_name: "Hopeful Heart", artist: "Dreamer", album: "Transitions", duration_ms: 210000, track_genre: "indie" },
                similarity_score: 0.88,
                alignment_score: 0.9,
                arc_score: 0.92,
                composite_score: 0.9,
                position: 1
              }
            ]
          }
        }
      ]);
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setUser(null);
    setHistoryItems([]);
  };

  const handleDeleteItem = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this prompt from your history?")) return;

    try {
      const { error } = await supabase
        .from("prompt_history")
        .delete()
        .eq("id", id);

      if (error) throw error;
      setHistoryItems(historyItems.filter(item => item.id !== id));
      if (expandedItemId === id) setExpandedItemId(null);
    } catch (e) {
      console.error("Failed to delete history item", e);
    }
  };

  const formatDate = (isoString: string) => {
    const d = new Date(isoString);
    return d.toLocaleDateString(undefined, { 
      month: "short", 
      day: "numeric", 
      hour: "2-digit", 
      minute: "2-digit" 
    });
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return "text-emerald-500 border-emerald-500/20 bg-emerald-500/5";
    if (score >= 0.5) return "text-amber-500 border-amber-500/20 bg-amber-500/5";
    return "text-rose-500 border-rose-500/20 bg-rose-500/5";
  };

  return (
    <div className="flex h-screen w-screen bg-black text-white font-sans overflow-hidden">
      {/* Sidebar Component */}
      <Sidebar 
        onReset={() => {}} 
        activeTab="history" 
        setActiveTab={() => {}} 
        user={user}
        savedPlaylists={savedPlaylists}
      />

      {/* Main content body */}
      <main className="flex-1 flex flex-col bg-zinc-950/70 m-2 ml-0 rounded-lg border border-zinc-900/80 overflow-hidden relative">
        
        {/* Header Bar */}
        <header className="h-20 flex items-center justify-between px-6 border-b border-zinc-900 bg-zinc-950/40 select-none z-10">
          <div className="flex items-center gap-3">
            <Link 
              href="/"
              className="w-10 h-10 bg-zinc-800 hover:bg-zinc-700/80 rounded-full flex items-center justify-center text-white transition flex-shrink-0"
              title="Back to Home"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <h1 className="text-xl font-bold tracking-tight text-white">Vibe Check History</h1>
          </div>

          {/* User Auth Info */}
          {user && (
            <div className="flex items-center gap-3 bg-black/40 hover:bg-zinc-900 border border-zinc-800 rounded-full py-1.5 pl-2.5 pr-4 transition group">
              {user.avatar_url ? (
                <img
                  src={user.avatar_url}
                  alt={user.display_name}
                  width={28}
                  height={28}
                  className="rounded-full border border-zinc-800"
                />
              ) : (
                <div className="w-7 h-7 rounded-full bg-emerald-500 flex items-center justify-center text-black font-bold text-xs">
                  {user.display_name.slice(0, 1).toUpperCase()}
                </div>
              )}
              <span className="text-white font-semibold text-xs truncate max-w-[120px]">
                {user.display_name}
              </span>
              <button
                onClick={handleLogout}
                className="ml-2 text-zinc-500 hover:text-rose-400 cursor-pointer"
                title="Sign out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          )}
        </header>

        {/* Scrollable history list */}
        <div className="flex-1 overflow-y-auto p-6 bg-gradient-to-b from-zinc-900/30 to-black/20">
          
          {/* Unauthenticated State */}
          {!user && !loading && (
            <div className="max-w-md mx-auto my-20 bg-zinc-900/60 border border-zinc-800 p-8 rounded-xl flex flex-col gap-5 items-center text-center backdrop-blur">
              <ShieldAlert className="w-14 h-14 text-emerald-400/80" />
              <div className="flex flex-col gap-2">
                <h3 className="text-white font-bold text-lg">Vibe Search History Locked</h3>
                <p className="text-zinc-400 text-xs leading-relaxed max-w-xs mx-auto">
                  Sign in with Google to view and manage your complete history of emotional music queries.
                </p>
              </div>
              <button
                onClick={handleLogin}
                className="bg-white text-black hover:bg-zinc-200 font-bold text-xs px-6 py-3 rounded-full transition cursor-pointer shadow-lg w-full"
              >
                Log in with Google
              </button>
            </div>
          )}

          {/* Loading Indicator */}
          {loading && (
            <div className="flex flex-col gap-4 max-w-4xl mx-auto py-12 animate-pulse">
              {[1, 2, 3].map((idx) => (
                <div key={idx} className="h-20 bg-zinc-900/40 rounded-xl w-full" />
              ))}
            </div>
          )}

          {/* History List */}
          {user && !loading && (
            <div className="max-w-4xl mx-auto flex flex-col gap-4">
              {historyItems.length === 0 ? (
                <div className="text-center py-20 flex flex-col items-center gap-4">
                  <Music className="w-12 h-12 text-zinc-600" />
                  <p className="text-zinc-500 text-sm">No vibe queries recorded yet.</p>
                  <Link 
                    href="/" 
                    className="bg-emerald-500 hover:bg-emerald-400 text-black font-extrabold text-xs px-5 py-2.5 rounded-full transition"
                  >
                    Check your first vibe
                  </Link>
                </div>
              ) : (
                historyItems.map((item) => {
                  const isExpanded = expandedItemId === item.id;
                  const queue: VibeQueue = item.queue_result;
                  const profile = item.emotional_profile;
                  
                  return (
                    <div 
                      key={item.id}
                      onClick={() => setExpandedItemId(isExpanded ? null : item.id)}
                      className={`bg-zinc-900/45 hover:bg-zinc-900/80 border transition-all duration-200 rounded-xl p-4 cursor-pointer select-none ${
                        isExpanded ? "border-zinc-800 bg-zinc-900/60 shadow-lg" : "border-zinc-900"
                      }`}
                    >
                      {/* Top Header Summary Row */}
                      <div className="flex justify-between items-center gap-4">
                        <div className="flex flex-col gap-1 min-w-0">
                          <span className="text-zinc-500 text-[10px] font-bold uppercase tracking-wider flex items-center gap-1.5">
                            <Clock className="w-3.5 h-3.5" />
                            <span>{formatDate(item.created_at)}</span>
                          </span>
                          <h3 className="text-white font-bold text-sm md:text-base truncate capitalize mt-1">
                            "{item.prompt_text}"
                          </h3>
                        </div>

                        {/* Badges and controls */}
                        <div className="flex items-center gap-3 flex-shrink-0">
                          <span className={`text-[9px] font-bold px-2 py-0.5 rounded border capitalize ${getConfidenceColor(item.confidence)}`}>
                            {Math.round(item.confidence * 100)}% Conf
                          </span>
                          
                          <button
                            onClick={(e) => handleDeleteItem(item.id, e)}
                            className="text-zinc-600 hover:text-rose-400 p-1.5 hover:bg-zinc-800 rounded transition cursor-pointer"
                            title="Delete query"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>

                          {isExpanded ? (
                            <ChevronUp className="w-5 h-5 text-zinc-400" />
                          ) : (
                            <ChevronDown className="w-5 h-5 text-zinc-400" />
                          )}
                        </div>
                      </div>

                      {/* Expanded Section Details */}
                      {isExpanded && queue && (
                        <div className="mt-5 border-t border-zinc-800/80 pt-5 flex flex-col gap-6" onClick={(e) => e.stopPropagation()}>
                          
                          {/* Inner Grid: Explanation & Profile Details */}
                          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                            {/* AI summary */}
                            <div className="md:col-span-3 bg-zinc-950/60 rounded-lg p-4 border border-zinc-900 relative overflow-hidden">
                              <span className="text-emerald-400 text-xs font-bold flex items-center gap-1">
                                <Sparkles className="w-3.5 h-3.5" />
                                <span>AI Insights</span>
                              </span>
                              <p className="text-zinc-300 text-xs leading-relaxed mt-2">
                                {queue.ai_explanation || "No explanation saved."}
                              </p>
                            </div>

                            {/* Transition profile */}
                            {profile && (
                              <div className="md:col-span-2 bg-zinc-950/60 rounded-lg p-4 border border-zinc-900 flex flex-col gap-2.5">
                                <span className="text-zinc-400 text-xs font-bold flex items-center gap-1.5">
                                  <Cpu className="w-3.5 h-3.5 text-zinc-500" />
                                  <span>Analysis</span>
                                </span>
                                <div className="flex flex-col gap-1.5 text-[11px]">
                                  <div className="flex justify-between">
                                    <span className="text-zinc-500 font-semibold">Mood Arc:</span>
                                    <span className="text-white font-bold capitalize">{profile.emotion_type?.replace(/_/g, " ")}</span>
                                  </div>
                                  <div className="flex justify-between items-center bg-zinc-900/60 p-1.5 rounded">
                                    <span className="text-zinc-500 font-bold uppercase tracking-wider text-[9px]">Current</span>
                                    <span className="text-white font-bold capitalize text-xs">{profile.current?.primary_emotion}</span>
                                    {profile.desired && (
                                      <>
                                        <ArrowRight className="w-3 h-3 text-emerald-400" />
                                        <span className="text-emerald-400 font-bold capitalize text-xs">{profile.desired?.primary_emotion}</span>
                                      </>
                                    )}
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>

                          {/* Track list */}
                          <div className="flex flex-col gap-1">
                            <span className="text-zinc-500 text-xs font-bold uppercase tracking-wider mb-2">Tracklist</span>
                            <div className="flex flex-col gap-1.5 max-h-[300px] overflow-y-auto scrollbar-thin pr-1">
                              {queue.tracks && queue.tracks.map((t, trackIdx) => (
                                <div key={t.track.id} className="grid grid-cols-[16px_4fr_3fr_100px] items-center gap-4 py-2 px-3 hover:bg-zinc-800/40 rounded transition text-zinc-300">
                                  <span className="text-zinc-600 text-xs font-bold">{trackIdx + 1}</span>
                                  <div className="flex flex-col min-w-0">
                                    <span className="text-white text-xs font-semibold truncate">{t.track.track_name}</span>
                                    <span className="text-zinc-500 text-[10px] truncate mt-0.5">{t.track.artist}</span>
                                  </div>
                                  <span className="text-zinc-400 text-xs truncate">{t.track.album}</span>
                                  <span className="text-zinc-500 text-[10px] font-mono text-right capitalize">{t.track.track_genre}</span>
                                </div>
                              ))}
                            </div>
                          </div>

                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          )}

        </div>
      </main>
    </div>
  );
}
