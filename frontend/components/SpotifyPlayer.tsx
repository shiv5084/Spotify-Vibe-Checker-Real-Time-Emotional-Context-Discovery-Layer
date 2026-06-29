import React, { useState, useEffect, useRef } from "react";
import { 
  Play, Pause, Shuffle, SkipBack, SkipForward, Repeat, 
  Mic2, ListMusic, Laptop, Volume2, Heart, Check, MoreHorizontal, Maximize2, Music,
  Copy, ExternalLink
} from "lucide-react";
import { Track } from "@/lib/types";

interface SpotifyPlayerProps {
  track: Track | null;
  isPlaying: boolean;
  setIsPlaying: React.Dispatch<React.SetStateAction<boolean>>;
  onPrev: () => void;
  onNext: () => void;
}

export default function SpotifyPlayer({
  track,
  isPlaying,
  setIsPlaying,
  onPrev,
  onNext
}: SpotifyPlayerProps) {
  const [shuffleActive, setShuffleActive] = useState(false);
  const [repeatActive, setRepeatActive] = useState(false);
  const [liked, setLiked] = useState(false);
  const [progress, setProgress] = useState(0); // in seconds
  const [duration, setDuration] = useState(0); // in seconds
  const [volume, setVolume] = useState(70); // 0 to 100
  const [showDropdown, setShowDropdown] = useState(false);
  const [copied, setCopied] = useState(false);
  const [isPlaybackPreview, setIsPlaybackPreview] = useState(false);

  const dropdownRef = useRef<HTMLDivElement>(null);
  const controllerRef = useRef<any>(null);
  const lastIsPausedRef = useRef<boolean | null>(null);
  const trackRef = useRef(track);

  // Synchronize track ref to avoid stale closures in event handlers
  useEffect(() => {
    trackRef.current = track;
  }, [track]);

  // Format seconds to MM:SS
  const formatTime = (seconds: number) => {
    if (isNaN(seconds) || seconds < 0) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
  };

  // Initialize Spotify Iframe API
  useEffect(() => {
    // 1. Asynchronously load script
    if (!(window as any).SpotifyIframeApi) {
      const script = document.createElement("script");
      script.src = "https://open.spotify.com/embed/iframe-api/v1";
      script.async = true;
      document.body.appendChild(script);
    }

    // 2. Define API Ready Callback
    const initController = (IFrameAPI: any) => {
      const element = document.getElementById("spotify-embed-root");
      if (!element) return;

      const options = {
        width: "100%",
        height: "80",
        uri: track ? `spotify:track:${track.id}` : "spotify:track:4uLU6hMCjMI75M1A2tKUQC"
      };

      IFrameAPI.createController(element, options, (EmbedController: any) => {
        controllerRef.current = EmbedController;

        // Force permission attributes on the generated iframe for audio streaming
        const iframe = element.querySelector("iframe");
        if (iframe) {
          iframe.setAttribute("allow", "autoplay; encrypted-media");
        }

        // Listen for playback updates
        EmbedController.addListener("playback_update", (e: any) => {
          const { position, duration: trackDur, isPaused } = e.data;
          setProgress(Math.floor(position / 1000));
          setDuration(Math.floor(trackDur / 1000));
          
          lastIsPausedRef.current = isPaused;

          // Detect preview limitation (user not signed in to Spotify)
          const currentTrack = trackRef.current;
          if (currentTrack && currentTrack.duration_ms > 45000 && Math.abs(trackDur - 30000) < 2000) {
            setIsPlaybackPreview(true);
          } else {
            setIsPlaybackPreview(false);
          }

          setIsPlaying((prevIsPlaying) => {
            if (prevIsPlaying === isPaused) {
              return !isPaused;
            }
            return prevIsPlaying;
          });
        });
      });
    };

    (window as any).onSpotifyIframeApiReady = (IFrameAPI: any) => {
      initController(IFrameAPI);
    };

    // If script is already loaded
    if ((window as any).SpotifyIframeApi && !controllerRef.current) {
      setTimeout(() => {
        initController((window as any).SpotifyIframeApi);
      }, 100);
    }
  }, []);

  // Update track when selection changes
  useEffect(() => {
    if (controllerRef.current && track) {
      lastIsPausedRef.current = null; // Reset controller state tracker on new track selection
      setIsPlaybackPreview(false); // Reset preview detection state
      controllerRef.current.loadUri(`spotify:track:${track.id}`);
      
      // Ensure iframe allow attributes are present after loadUri
      const element = document.getElementById("spotify-embed-root");
      const iframe = element?.querySelector("iframe");
      if (iframe) {
        iframe.setAttribute("allow", "autoplay; encrypted-media");
      }

      // Autoplay if isPlaying was already active
      if (isPlaying) {
        setTimeout(() => {
          controllerRef.current?.play();
        }, 150);
      }
    }
  }, [track?.id]);

  // Synchronize Playback Command States (Play/Pause toggles)
  useEffect(() => {
    if (!controllerRef.current) return;
    
    // Bypass play/pause instructions if the controller matches current play state
    const isPausedOnController = lastIsPausedRef.current;
    if (isPausedOnController !== null) {
      const isPlayingOnController = !isPausedOnController;
      if (isPlaying === isPlayingOnController) {
        return; // Already in sync, do not issue duplicate instructions
      }
    }

    if (isPlaying) {
      controllerRef.current.play();
    } else {
      controllerRef.current.pause();
    }
  }, [isPlaying]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Copy the track's Spotify URL link to clipboard
  const handleCopyLink = async () => {
    if (!track) return;
    try {
      const url = `https://open.spotify.com/track/${track.id}`;
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy link:", err);
    }
  };

  // Open the track in Spotify web player in a new tab
  const handleOpenSpotify = () => {
    if (!track) return;
    window.open(`https://open.spotify.com/track/${track.id}`, "_blank", "noopener,noreferrer");
    setShowDropdown(false);
  };

  // Handle Play/Pause toggle button
  const handlePlayPause = () => {
    if (!track || !controllerRef.current) return;
    controllerRef.current.togglePlay();
  };

  // Handle progress click/seek
  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!controllerRef.current || duration === 0) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const percentage = clickX / rect.width;
    const newPositionSec = Math.floor(percentage * duration);
    setProgress(newPositionSec);
    controllerRef.current.seek(newPositionSec);
  };

  // Handle volume bar click simulation
  const handleVolumeClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const percentage = Math.max(0, Math.min(1, clickX / rect.width));
    setVolume(Math.round(percentage * 100));
  };

  return (
    <div className="flex flex-col w-full z-40 select-none">
      
      {/* Spotify Embed IFrame serving as the audible audio engine */}
      <div 
        className="w-full bg-[#121212] transition-all duration-350 overflow-hidden border-t border-zinc-800/80"
        style={{ height: track ? "80px" : "0px" }}
      >
        <div id="spotify-embed-root" className="w-full h-full" />
      </div>

      {/* Spotify Sign-in Warning Banner (rendered only when preview is detected) */}
      {isPlaybackPreview && (
        <div className="bg-rose-500/10 border-t border-rose-500/20 px-5 py-2.5 flex items-center justify-between text-xs text-rose-400 font-semibold animate-fadeIn">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse" />
            <span>Sign in to Spotify Free account to listen to the full track</span>
          </div>
          <a 
            href="https://open.spotify.com" 
            target="_blank" 
            rel="noopener noreferrer" 
            className="hover:underline font-bold text-rose-300 flex items-center gap-1 cursor-pointer"
          >
            Sign In on Spotify →
          </a>
        </div>
      )}

      {/* Custom Bottom Playbar UI - Desktop Only */}
      <div className="hidden md:flex flex-col bg-[#181818] border-t border-zinc-850 px-5 py-4 text-zinc-100 gap-1 shadow-2xl w-full">

      {/* Main control bar Layout */}
      <div className="flex md:grid md:grid-cols-3 items-center justify-between gap-4">
        
        {/* LEFT COLUMN: Metadata & Option Controls */}
        <div className="flex items-center gap-2.5 md:gap-3.5 min-w-0 flex-1 md:flex-initial">
          {track ? (
            <>
              <div className="w-10 h-10 md:w-14 md:h-14 bg-zinc-800 rounded flex-shrink-0 flex items-center justify-center font-bold text-xs md:text-sm text-zinc-400 border border-zinc-700/30 overflow-hidden relative shadow-md">
                <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-indigo-500/10 opacity-50" />
                {track.track_name.slice(0, 2).toUpperCase()}
              </div>
              <div className="flex flex-col min-w-0">
                <span className="text-white text-xs md:text-sm font-semibold hover:underline cursor-pointer truncate">
                  {track.track_name}
                </span>
                <span className="text-zinc-400 text-[10px] md:text-xs hover:underline cursor-pointer truncate mt-0.5 font-medium">
                  {track.artist}
                </span>
              </div>
            </>
          ) : (
            <>
              <div className="w-10 h-10 md:w-14 md:h-14 bg-zinc-800/60 rounded flex-shrink-0 flex items-center justify-center text-zinc-500 border border-zinc-800/80 shadow-md">
                <Music className="w-5 h-5 md:w-6 md:h-6 animate-pulse" />
              </div>
              <div className="flex flex-col min-w-0">
                <span className="text-zinc-400 text-xs md:text-sm font-semibold truncate">
                  No track playing
                </span>
                <span className="text-zinc-550 text-[10px] md:text-xs truncate mt-0.5 font-medium">
                  Select a vibe
                </span>
              </div>
            </>
          )}

          {/* Option Menu Controls with Dropdown */}
          <div 
            ref={dropdownRef}
            className={`hidden sm:flex items-center gap-2.5 ml-4 ${!track ? "opacity-30 pointer-events-none" : ""}`}
          >
            <button 
              onClick={() => setLiked(!liked)} 
              className={`transition hover:scale-105 ${liked ? "text-emerald-500 hover:text-emerald-455" : "text-zinc-400 hover:text-white"}`}
              title="Save to Library"
            >
              <Heart className={`w-4 h-4 ${liked ? "fill-emerald-500" : ""}`} />
            </button>
            <button className="text-zinc-400 hover:text-white transition hover:scale-105" title="Add to Playlist">
              <Check className="w-4 h-4" />
            </button>
            
            <button 
              onClick={() => setShowDropdown(!showDropdown)}
              className={`text-zinc-400 hover:text-white transition hover:scale-105 ${showDropdown ? "text-white scale-105" : ""}`} 
              title="More Options"
            >
              <MoreHorizontal className="w-4 h-4" />
            </button>

            {/* Dropdown Menu Popup */}
            {showDropdown && (
              <div className="absolute bottom-full left-0 mb-3 w-48 bg-[#282828] border border-zinc-700/80 rounded-md shadow-2xl z-50 py-1 text-xs select-none animate-in fade-in slide-in-from-bottom-2 duration-150">
                <button
                  onClick={handleCopyLink}
                  className="w-full text-left px-3.5 py-2.5 text-zinc-200 hover:bg-zinc-700/70 hover:text-white flex items-center gap-2 transition"
                >
                  <Copy className="w-3.5 h-3.5" />
                  <span>{copied ? "Copied Link!" : "Copy Spotify Link"}</span>
                </button>
                <button
                  onClick={handleOpenSpotify}
                  className="w-full text-left px-3.5 py-2.5 text-zinc-200 hover:bg-zinc-700/70 hover:text-white flex items-center gap-2 transition border-t border-zinc-750"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>Open in Spotify</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Mobile Play/Pause Controls */}
        <div className="flex md:hidden items-center gap-3">
          {track && (
            <button 
              onClick={handlePlayPause}
              className="w-8 h-8 rounded-full bg-white text-black flex items-center justify-center transition active:scale-90"
              title={isPlaying ? "Pause" : "Play"}
            >
              {isPlaying ? (
                <Pause className="w-4 h-4 fill-black text-black" />
              ) : (
                <Play className="w-4 h-4 fill-black text-black ml-0.5" />
              )}
            </button>
          )}
        </div>

        {/* CENTER COLUMN: Playback / Transport Controls & Timers */}
        <div className="hidden md:flex flex-col items-center gap-2 w-full">
          {/* Controls row */}
          <div className={`flex items-center gap-5 ${!track ? "opacity-30 pointer-events-none" : ""}`}>
            <button 
              onClick={() => setShuffleActive(!shuffleActive)}
              className={`transition hover:scale-105 active:scale-95 ${shuffleActive ? "text-emerald-500 hover:text-emerald-400" : "text-zinc-400 hover:text-white"}`}
              title="Shuffle"
            >
              <Shuffle className="w-4 h-4" />
            </button>
            
            <button 
              onClick={onPrev}
              className="text-zinc-400 hover:text-white transition hover:scale-105 active:scale-95"
              title="Previous"
            >
              <SkipBack className="w-4.5 h-4.5 fill-current" />
            </button>
            
            <button 
              onClick={handlePlayPause}
              className="w-8 h-8 rounded-full bg-white text-black flex items-center justify-center hover:scale-105 active:scale-95 transition shadow-md"
              title={isPlaying ? "Pause" : "Play"}
            >
              {isPlaying ? (
                <Pause className="w-4.5 h-4.5 fill-black text-black ml-0" />
              ) : (
                <Play className="w-4.5 h-4.5 fill-black text-black ml-0.5" />
              )}
            </button>
            
            <button 
              onClick={onNext}
              className="text-zinc-400 hover:text-white transition hover:scale-105 active:scale-95"
              title="Next"
            >
              <SkipForward className="w-4.5 h-4.5 fill-current" />
            </button>
            
            <button 
              onClick={() => setRepeatActive(!repeatActive)}
              className={`transition hover:scale-105 active:scale-95 ${repeatActive ? "text-emerald-500 hover:text-emerald-400" : "text-zinc-400 hover:text-white"}`}
              title="Repeat"
            >
              <Repeat className="w-4.5 h-4.5" />
            </button>
          </div>

          {/* Progress Slider */}
          <div className={`flex items-center gap-2.5 w-full max-w-md text-[10px] text-zinc-400 font-mono font-medium ${!track ? "opacity-35 pointer-events-none" : ""}`}>
            <span className="w-8 text-right">{formatTime(progress)}</span>
            <div 
              onClick={handleProgressClick}
              className="flex-1 h-1 bg-zinc-700 hover:h-1.5 rounded-full overflow-hidden cursor-pointer transition-all duration-100 group relative"
            >
              <div 
                className="h-full bg-white group-hover:bg-emerald-500 rounded-full" 
                style={{ width: duration > 0 ? `${(progress / duration) * 100}%` : "0%" }}
              />
            </div>
            <span className="w-8 text-left">{formatTime(duration)}</span>
          </div>
        </div>

        {/* RIGHT COLUMN: Utility Panels */}
        <div className="hidden md:flex items-center justify-end gap-3.5">
          <button className="text-zinc-400 hover:text-white transition" title="Lyrics">
            <Mic2 className="w-4 h-4" />
          </button>
          <button className="text-zinc-400 hover:text-white transition" title="Queue">
            <ListMusic className="w-4 h-4" />
          </button>
          <button className="text-zinc-400 hover:text-white transition" title="Connect to a device">
            <Laptop className="w-4 h-4" />
          </button>
          <div className="flex items-center gap-2 group">
            <button className="text-zinc-400 hover:text-white transition">
              <Volume2 className="w-4 h-4" />
            </button>
            <div 
              onClick={handleVolumeClick}
              className="w-20 h-1 bg-zinc-750 rounded-full overflow-hidden cursor-pointer group-hover:bg-zinc-700"
            >
              <div 
                className="h-full bg-white group-hover:bg-emerald-500 rounded-full" 
                style={{ width: `${volume}%` }}
              />
            </div>
          </div>
          <button className="text-zinc-400 hover:text-white transition hidden md:block" title="Fullscreen">
            <Maximize2 className="w-4 h-4" />
          </button>
        </div>

      </div>
    </div>
  </div>
);
}
