"use client";

import React, { useState, useEffect, useRef } from "react";
import Image from "next/image";
import { 
  Plus, Music, Search, ArrowRight, Loader2, Sparkles, User, 
  LogOut, AlertCircle, RefreshCw, Star, Compass, Play, Check, Home as HomeIcon, Menu
} from "lucide-react";
import { supabase } from "@/lib/supabase";
import { fetchWithAuth } from "@/lib/api";
import { VibeQueue, UserProfile, Track } from "@/lib/types";
import Sidebar from "@/components/Sidebar";
import VibeInput from "@/components/VibeInput";
import QueueResults from "@/components/QueueResults";
import SpotifyLanding from "@/components/SpotifyLanding";
import SpotifyPlayer from "@/components/SpotifyPlayer";

export default function Home() {
  const [activeTab, setActiveTab] = useState("home");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [session, setSession] = useState<any>(null);
  
  // Pipeline prompt states
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<{ message: string; suggestion: string } | null>(null);
  const [vibeQueue, setVibeQueue] = useState<VibeQueue | null>(null);
  
  // Local list of saved vibe playlists (persisted in localStorage)
  const [savedPlaylists, setSavedPlaylists] = useState<any[]>([]);
  
  // Anonymous counter
  const [anonCount, setAnonCount] = useState(0);

  // Global Player States
  const [currentTrack, setCurrentTrack] = useState<Track | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentQueue, setCurrentQueue] = useState<any[]>([]);

  // Synchronize queue when vibeQueue is loaded
  useEffect(() => {
    if (vibeQueue) {
      setCurrentQueue(vibeQueue.tracks);
    }
  }, [vibeQueue]);

  // Load active session and auth listeners on mount
  useEffect(() => {
    // Clean up URL hash if it contains access_token from Supabase redirection
    if (typeof window !== "undefined" && window.location.hash.includes("access_token=")) {
      window.history.replaceState(null, "", window.location.pathname + window.location.search);
    }

    // Load anon usage count
    const count = localStorage.getItem("vibe_checker_anon_usage");
    if (count) {
      setAnonCount(parseInt(count, 10));
    }

    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session?.user) {
        setUser({
          id: session.user.id,
          email: session.user.email || "",
          display_name: session.user.user_metadata.full_name || session.user.user_metadata.name || "Vibe User",
          avatar_url: session.user.user_metadata.avatar_url || null
        });
      }
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      if (session?.user) {
        setUser({
          id: session.user.id,
          email: session.user.email || "",
          display_name: session.user.user_metadata.full_name || session.user.user_metadata.name || "Vibe User",
          avatar_url: session.user.user_metadata.avatar_url || null
        });
      } else {
        setUser(null);
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

  // Handle Google Login
  const handleLogin = async () => {
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: typeof window !== "undefined" ? window.location.origin : "",
        }
      });
      if (error) throw error;
    } catch (err: any) {
      console.error("Sign-in failed", err.message);
      // Mock login for offline development/testing
      const mockUser: UserProfile = {
        id: "mock-user-12345",
        email: "demo@vibechecker.com",
        display_name: "Demo Vibe User",
        avatar_url: null
      };
      setUser(mockUser);
      localStorage.setItem("vibe_checker_mock_user", JSON.stringify(mockUser));
    }
  };

  // Handle Logout
  const handleLogout = async () => {
    await supabase.auth.signOut();
    setUser(null);
    localStorage.removeItem("vibe_checker_mock_user");
  };

  // Handle prompt submissions
  const handleBuildQueue = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setLoading(true);
    setError(null);
    setVibeQueue(null);

    try {
      const result = await fetchWithAuth("vibe", {
        method: "POST",
        body: JSON.stringify({ prompt })
      });

      setVibeQueue(result);

      // Increment anon count if not authenticated
      if (!user) {
        const nextCount = anonCount + 1;
        setAnonCount(nextCount);
        localStorage.setItem("vibe_checker_anon_usage", nextCount.toString());
      }
    } catch (err: any) {
      setError({
        message: err.message || "An unexpected error occurred.",
        suggestion: err.suggestion || "Please try again later."
      });
      // Synchronize the local trials counter if the backend indicates the limit is reached
      if (err.message && err.message.includes("Free trial limit reached")) {
        setAnonCount(3);
        localStorage.setItem("vibe_checker_anon_usage", "3");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setPrompt(suggestion);
  };

  const handleSavePlaylist = async (name: string) => {
    if (!vibeQueue || !user) return;
    
    // Add to local state and persist
    const newPlaylist = {
      name: `${prompt} Vibe`,
      emotion_type: vibeQueue.emotion_type,
      tracks_count: vibeQueue.tracks.length,
      created_at: new Date().toISOString()
    };

    const updated = [newPlaylist, ...savedPlaylists];
    setSavedPlaylists(updated);
    localStorage.setItem(`vibe_checker_saved_playlists_${user.id}`, JSON.stringify(updated));
  };

  const handleReset = () => {
    setPrompt("");
    setVibeQueue(null);
    setError(null);
  };

  const playTrack = (track: Track) => {
    if (currentTrack?.id === track.id) {
      setIsPlaying(!isPlaying);
    } else {
      setCurrentTrack(track);
      setIsPlaying(true);
    }
  };

  const handlePrev = () => {
    if (!currentTrack || currentQueue.length === 0) return;
    const currentIndex = currentQueue.findIndex((t) => t.track.id === currentTrack.id);
    if (currentIndex > 0) {
      setCurrentTrack(currentQueue[currentIndex - 1].track);
      setIsPlaying(true);
    } else {
      setCurrentTrack(currentQueue[currentQueue.length - 1].track);
      setIsPlaying(true);
    }
  };

  const handleNext = () => {
    if (!currentTrack || currentQueue.length === 0) return;
    const currentIndex = currentQueue.findIndex((t) => t.track.id === currentTrack.id);
    if (currentIndex < currentQueue.length - 1) {
      setCurrentTrack(currentQueue[currentIndex + 1].track);
      setIsPlaying(true);
    } else {
      setCurrentTrack(currentQueue[0].track);
      setIsPlaying(true);
    }
  };

  const authPanel = (
    <div className="flex items-center gap-2 md:gap-4 flex-shrink-0">
      {/* Anonymous Trial Counter */}
      {!user && anonCount > 0 && (
        <span className="text-zinc-550 text-[10px] md:text-xs font-semibold whitespace-nowrap">
          Trial: {anonCount} of 3
        </span>
      )}

      {user ? (
        /* Signed-In: Profile Avatar */
        <div className="flex items-center gap-2 md:gap-3 bg-black/40 hover:bg-zinc-900 border border-zinc-800 rounded-full py-1 pl-2.5 pr-3 md:py-1.5 md:pl-2.5 md:pr-4 transition group relative">
          {user.avatar_url ? (
            <Image
              src={user.avatar_url}
              alt={user.display_name}
              width={24}
              height={24}
              className="rounded-full border border-zinc-800 w-6 h-6 md:w-7 md:h-7"
            />
          ) : (
            <div className="w-6 h-6 md:w-7 md:h-7 rounded-full bg-emerald-500 flex items-center justify-center text-black font-bold text-[10px] md:text-xs flex-shrink-0">
              {user.display_name.slice(0, 1).toUpperCase()}
            </div>
          )}
          <span className="text-white font-semibold text-[10px] md:text-xs truncate max-w-[70px] md:max-w-[100px]">
            {user.display_name}
          </span>

          {/* Logout Tooltip */}
          <button
            onClick={handleLogout}
            className="ml-1 md:ml-2 text-zinc-500 hover:text-rose-400 cursor-pointer"
            title="Sign out"
          >
            <LogOut className="w-3.5 h-3.5 md:w-4 h-4" />
          </button>
        </div>
      ) : (
        /* Signed-Out: Log in Buttons (Screen 1) */
        <button
          onClick={handleLogin}
          className="bg-white text-black hover:bg-zinc-200 font-bold text-[10px] md:text-xs px-3.5 py-1.5 md:px-5 md:py-2 rounded-full transition cursor-pointer"
        >
          Log in
        </button>
      )}
    </div>
  );

  return (
    <div className="flex flex-col h-dvh w-screen bg-black text-white font-sans overflow-hidden">
      <div className="flex flex-1 h-0 relative">
        {/* Sidebar Component */}
        <Sidebar 
          onReset={handleReset} 
          activeTab={activeTab} 
          setActiveTab={setActiveTab} 
          user={user}
          savedPlaylists={savedPlaylists}
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />

        {/* Main content body */}
        <main className="flex-1 flex flex-col bg-zinc-950/70 m-1 md:m-2 md:ml-0 rounded-lg border border-zinc-900/80 overflow-hidden relative">
          
          {/* Spotify Persistent Header Bar */}
          <header className="flex flex-col md:flex-row md:h-20 items-stretch md:items-center justify-between px-4 md:px-6 py-3 md:py-0 border-b border-zinc-900 bg-zinc-950/40 select-none z-10 gap-3 md:gap-6">
            
            {/* Row 1 / Main row content */}
            <div className="flex items-center justify-between md:justify-start gap-4 flex-1 min-w-0">
              
              {/* Mobile hamburger toggle + Logo */}
              <div className="flex items-center gap-2 md:gap-3">
                {/* Hamburger button for mobile */}
                <button
                  type="button"
                  onClick={() => setSidebarOpen(true)}
                  className="p-1 text-zinc-400 hover:text-white md:hidden hover:bg-zinc-800 rounded transition cursor-pointer"
                  aria-label="Open sidebar"
                >
                  <Menu className="w-5.5 h-5.5" />
                </button>

                {/* 1. Spotify Logo */}
                <div 
                  onClick={handleReset} 
                  className="flex items-center gap-2 cursor-pointer hover:scale-[1.02] transition flex-shrink-0"
                  title="Spotify Home"
                >
                  <svg viewBox="0 0 24 24" className="w-6 h-6 md:w-8 md:h-8 fill-white">
                    <path d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2zm4.586 14.424c-.18.295-.565.387-.86.207-2.377-1.454-5.37-1.783-8.893-.982-.336.075-.668-.135-.744-.47-.077-.337.135-.668.47-.745 3.856-.88 7.15-.5 9.822 1.135.296.18.387.563.205.855zm1.225-2.72c-.228.368-.713.49-1.08.262-2.717-1.67-6.86-2.155-10.065-1.183-.413.125-.847-.107-.972-.52-.125-.413.108-.847.52-.972 3.665-1.112 8.225-.572 11.335 1.343.366.226.49.712.262 1.08zm.105-2.81c-3.258-1.933-8.636-2.113-11.75-.163-.5.15-.99-.12-1.14-.62-.15-.5.12-.99.62-1.14 3.626-1.1 9.54-.89 13.3 1.34.45.27.6.85.33 1.3-.27.45-.85.6-1.3.33z"/>
                  </svg>
                  <span className="font-black text-sm md:text-lg tracking-tighter text-white">Spotify</span>
                </div>

                {/* 2. Home Page Logo/Button */}
                <button 
                  onClick={handleReset} 
                  className="w-8 h-8 md:w-10 md:h-10 bg-zinc-800 hover:bg-zinc-700/80 rounded-full flex items-center justify-center text-white transition flex-shrink-0"
                  title="Home"
                >
                  <HomeIcon className="w-4.5 h-4.5 md:w-5 md:h-5 fill-white text-white" />
                </button>
              </div>

              {/* Inlined Vibe Checker Input (md+ only) */}
              <div className="hidden md:block flex-1 max-w-lg">
                <VibeInput
                  prompt={prompt}
                  setPrompt={setPrompt}
                  onSubmit={handleBuildQueue}
                  loading={loading}
                  onSuggestionClick={handleSuggestionClick}
                />
              </div>

              {/* Search Bar - hidden on mobile, visible only on large screen */}
              <div className="hidden lg:flex relative items-center bg-zinc-800/60 hover:bg-zinc-800 rounded-full py-2 px-3.5 w-44 xl:w-56 select-none cursor-not-allowed flex-shrink-0">
                <Search className="w-3.5 h-3.5 text-zinc-500 mr-2 flex-shrink-0" />
                <span className="text-zinc-500 text-xs truncate font-semibold">Search artists...</span>
              </div>

              {/* Mobile Auth Panel */}
              <div className="flex md:hidden items-center">
                {authPanel}
              </div>
            </div>

            {/* Mobile Vibe Checker Input (below header content on mobile) */}
            <div className="block md:hidden w-full pb-1">
              <VibeInput
                prompt={prompt}
                setPrompt={setPrompt}
                onSubmit={handleBuildQueue}
                loading={loading}
                onSuggestionClick={handleSuggestionClick}
              />
            </div>

            {/* Desktop Auth Panel */}
            <div className="hidden md:flex items-center ml-4 flex-shrink-0">
              {authPanel}
            </div>
          </header>

        {/* Dashboard Panels Scrollable Body */}
        <div className="flex-1 overflow-y-auto p-6 bg-gradient-to-b from-zinc-900/30 to-black/20">
          
          {/* SKELETON LOADING STATE (Stage transitions) */}
          {loading && (
            <div className="flex flex-col gap-6 max-w-4xl mx-auto py-12 animate-pulse">
              <div className="flex justify-between items-center pb-6 border-b border-zinc-900">
                <div className="flex flex-col gap-2">
                  <div className="h-4 bg-zinc-800 rounded w-24" />
                  <div className="h-8 bg-zinc-800 rounded w-64" />
                </div>
                <div className="h-10 bg-zinc-800 rounded-full w-32" />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
                <div className="md:col-span-3 h-32 bg-zinc-900/60 rounded-xl" />
                <div className="md:col-span-2 h-32 bg-zinc-900/60 rounded-xl" />
              </div>
              <div className="flex flex-col gap-4 mt-6">
                {[1, 2, 3, 4, 5].map((idx) => (
                  <div key={idx} className="h-12 bg-zinc-900/40 rounded-lg w-full" />
                ))}
              </div>
            </div>
          )}

          {/* ERROR EMATHETIC DISPLAY */}
          {error && !loading && (
            <div className="max-w-md mx-auto my-12 bg-zinc-900/80 border border-rose-500/20 p-6 rounded-xl flex flex-col gap-4 items-center text-center backdrop-blur">
              <AlertCircle className="w-12 h-12 text-rose-500" />
              <div className="flex flex-col gap-1.5">
                <h4 className="text-white font-bold text-base">{error.message}</h4>
                <p className="text-zinc-400 text-xs leading-relaxed">{error.suggestion}</p>
              </div>
              <div className="flex gap-3 mt-2 w-full">
                <button
                  onClick={handleReset}
                  className="flex-1 bg-zinc-800 hover:bg-zinc-700 text-white text-xs font-bold py-2 rounded-full transition cursor-pointer"
                >
                  Clear Prompt
                </button>
                {!user && (
                  <button
                    onClick={handleLogin}
                    className="flex-1 bg-emerald-500 hover:bg-emerald-400 text-black text-xs font-bold py-2 rounded-full transition cursor-pointer"
                  >
                    Log In with Google
                  </button>
                )}
              </div>
            </div>
          )}

          {/* SCREEN 1: LANDING PAGE (Empty Search State) - Spotify Landing Page */}
          {!loading && !error && !vibeQueue && (
            <SpotifyLanding onPlayDemo={handleSuggestionClick} />
          )}

          {/* SCREEN 3: RESULTS STATE (Generated Vibe Playlist) */}
          {vibeQueue && !loading && !error && (
            <QueueResults 
              queue={vibeQueue} 
              onSave={handleSavePlaylist} 
              user={user}
              playingTrackId={currentTrack?.id || null}
              isPlaying={isPlaying}
              onPlayToggle={playTrack}
            />
          )}

        </div>
      </main>
    </div>

    {/* Persistent Bottom Spotify Player Bar */}
    <SpotifyPlayer
      track={currentTrack}
      isPlaying={isPlaying}
      setIsPlaying={setIsPlaying}
      onPrev={handlePrev}
      onNext={handleNext}
    />
  </div>
  );
}
