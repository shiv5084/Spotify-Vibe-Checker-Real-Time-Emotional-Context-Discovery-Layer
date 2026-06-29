import React from "react";
import Link from "next/link";
import { Home, Search, Library, Plus, Heart, Music, History, X } from "lucide-react";

interface SidebarProps {
  onReset: () => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  user: any;
  savedPlaylists: any[];
  isOpen?: boolean;
  onClose?: () => void;
}

export default function Sidebar({ onReset, activeTab, setActiveTab, user, savedPlaylists, isOpen = false, onClose }: SidebarProps) {
  return (
    <>
      {/* Backdrop for mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/60 z-40 md:hidden"
          onClick={onClose}
        />
      )}
      
      <aside 
        className={`w-64 bg-black flex flex-col gap-2 p-2 select-none h-full text-zinc-400 font-sans fixed inset-y-0 left-0 z-50 transform transition-transform duration-300 ease-in-out md:relative md:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Library Panel */}
        <div className="bg-zinc-900 rounded-lg flex-1 p-5 flex flex-col gap-4 overflow-hidden relative">
          
          {/* Close button for mobile */}
          {onClose && (
            <button 
              onClick={onClose} 
              className="absolute top-4 right-4 text-zinc-400 hover:text-white md:hidden transition"
              aria-label="Close sidebar"
            >
              <X className="w-5 h-5" />
            </button>
          )}

          {/* Navigation Block */}
          <div className="flex flex-col gap-1 border-b border-zinc-800/80 pb-3 mt-4 md:mt-0">
            <Link 
              href="/"
              onClick={() => {
                onReset();
                if (onClose) onClose();
              }}
              className={`flex items-center gap-3 font-semibold p-2.5 rounded-lg hover:text-white transition cursor-pointer ${
                activeTab === "home" ? "text-white bg-zinc-800/60" : "text-zinc-400"
              }`}
            >
              <Home className="w-5 h-5" />
              <span className="text-sm">Home Dashboard</span>
            </Link>
            <Link 
              href="/history"
              onClick={() => {
                if (onClose) onClose();
              }}
              className={`flex items-center gap-3 font-semibold p-2.5 rounded-lg hover:text-white transition cursor-pointer ${
                activeTab === "history" ? "text-white bg-zinc-800/60" : "text-zinc-400"
              }`}
            >
              <History className="w-5 h-5" />
              <span className="text-sm">Vibe History</span>
            </Link>
          </div>

        <div className="flex items-center justify-between text-zinc-400">
          <div className="flex items-center gap-3 font-semibold hover:text-white transition cursor-pointer">
            <Library className="w-6 h-6" />
            <span>Your Library</span>
          </div>
          <button className="hover:text-white transition p-1 hover:bg-zinc-800 rounded-full">
            <Plus className="w-5 h-5" />
          </button>
        </div>


        {/* Playlist Filters */}
        <div className="flex gap-2">
          <span className="bg-zinc-800 text-white text-xs font-semibold px-3 py-1.5 rounded-full cursor-pointer hover:bg-zinc-700 transition">
            Playlists
          </span>
          <span className="bg-zinc-800 text-white text-xs font-semibold px-3 py-1.5 rounded-full cursor-pointer hover:bg-zinc-700 transition">
            Vibes
          </span>
        </div>

        {/* Playlists List */}
        <div className="flex-1 overflow-y-auto flex flex-col gap-3 pr-1 scrollbar-thin">
          <div className="flex items-center gap-3 p-2 hover:bg-zinc-800/50 rounded-md cursor-pointer transition">
            <div className="w-12 h-12 bg-gradient-to-br from-indigo-700 to-purple-900 rounded flex items-center justify-center text-white">
              <Heart className="w-6 h-6 fill-white" />
            </div>
            <div className="flex flex-col">
              <span className="text-white font-medium text-sm">Liked Songs</span>
              <span className="text-xs text-zinc-500">Playlist • 142 songs</span>
            </div>
          </div>

          {/* User's saved vibe playlists */}
          {user && savedPlaylists.map((pl, idx) => (
            <div key={idx} className="flex items-center gap-3 p-2 hover:bg-zinc-800/50 rounded-md cursor-pointer transition">
              <div className="w-12 h-12 bg-zinc-800 rounded flex items-center justify-center text-white border border-zinc-700/50 font-bold text-xs uppercase">
                {pl.emotion_type?.slice(0, 3) || "VIB"}
              </div>
              <div className="flex flex-col overflow-hidden">
                <span className="text-white font-medium text-sm truncate">{pl.name}</span>
                <span className="text-xs text-zinc-500 truncate">Vibe Queue • {pl.tracks_count} tracks</span>
              </div>
            </div>
          ))}

          {/* Placeholder for offline playlists */}
          {user && savedPlaylists.length === 0 && (
            <div className="text-zinc-600 text-xs text-center py-8">
              No saved vibe playlists yet.<br />Submit a prompt and save your first queue!
            </div>
          )}

          {/* Message for signed-out users */}
          {!user && (
            <div className="text-zinc-600 text-xs text-center py-8">
              Sign in with Google to save and view your vibe playlists.
            </div>
          )}
        </div>
      </div>
    </aside>
    </>
  );
}
