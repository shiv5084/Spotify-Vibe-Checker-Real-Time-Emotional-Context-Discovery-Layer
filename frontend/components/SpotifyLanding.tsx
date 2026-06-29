import React from "react";
import Image from "next/image";
import { Play } from "lucide-react";

interface SpotifyLandingProps {
  onPlayDemo: (prompt: string) => void;
}

export default function SpotifyLanding({ onPlayDemo }: SpotifyLandingProps) {
  // Filter chips list
  const chips = ["All", "Music", "Podcasts"];
  const [activeChip, setActiveChip] = React.useState("All");

  // Mock album cards data with high-quality Unsplash image IDs to match user's screenshot
  const popularAlbums = [
    {
      title: "Aashiqui 2",
      desc: "Mithoon, Ankit Tiwari, Jeet Gannguli",
      image: "https://images.unsplash.com/photo-1518199266791-5375a83190b7?w=300&q=80", // Couple under jacket style
      prompt: "Feeling heartbroken, need emotional romantic songs"
    },
    {
      title: "Finding Her",
      desc: "Kushagra, Bharath, Saaheal",
      image: "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=300&q=80", // Guy in grass style
      prompt: "Introspective acoustic folk mood"
    },
    {
      title: "Sanam Teri Kasam",
      desc: "Himesh Reshammiya, Sameer Anjaan, Subrat...",
      image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=300&q=80", // Romantic hug style
      prompt: "Melancholic love songs"
    },
    {
      title: "Raanjhan (From \"Do Patti\")",
      desc: "Sachet-Parampara, Parampara Tandon, Kaus...",
      image: "https://images.unsplash.com/photo-1464746133101-a2c3f88e0dd9?w=300&q=80", // Couple close-up style
      prompt: "Soft emotional Bollywood tracks"
    },
    {
      title: "Ultimate Love Songs Arijit Singh",
      desc: "Arijit Singh",
      image: "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=300&q=80", // Singer style
      prompt: "Arijit Singh emotional transition"
    }
  ];

  const recommendedPlaylists = [
    {
      title: "Yo Hai Haryanvi",
      desc: "Biggest Haryanvi hits from the last 10 years.",
      image: "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&q=80",
      prompt: "Haryanvi energetic beats"
    },
    {
      title: "Kollywood Cream",
      desc: "Finest collection of Tamil Music from the past 10...",
      image: "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300&q=80",
      prompt: "Tamil emotional melodies"
    },
    {
      title: "Tollywood Pearls",
      desc: "The finest set of Telugu music from the past 10...",
      image: "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300&q=80",
      prompt: "Telugu acoustic vibe"
    },
    {
      title: "I-Pop Icons",
      desc: "Hottest tracks from your favourite I-Pop Icons....",
      image: "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=300&q=80",
      prompt: "Indian pop party hits"
    },
    {
      title: "Indie India",
      desc: "Best of the Indian Indie scene. Cover - Gini",
      image: "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=300&q=80",
      prompt: "Indian indie chill acoustic vibe"
    },
    {
      title: "Bollywood Central",
      desc: "Bollywood Central, jab baje toh seedha dil ke...",
      image: "https://images.unsplash.com/photo-1540910419892-4a36d2c3266c?w=300&q=80",
      prompt: "Bollywood emotional hits"
    },
    {
      title: "Punjabi 101",
      desc: "Ultimate 101 Punjabi Hits with Navaan Sandhu",
      image: "https://images.unsplash.com/photo-1498038432885-c6f3f1b912ee?w=300&q=80",
      prompt: "Punjabi high energy beats"
    }
  ];

  return (
    <div className="flex flex-col gap-8 select-none font-sans text-zinc-100 max-w-7xl mx-auto w-full">
      
      {/* Pills Filter Chips */}
      <div className="flex items-center gap-2">
        {chips.map((chip) => (
          <button
            key={chip}
            onClick={() => setActiveChip(chip)}
            className={`text-xs font-bold px-3 py-2 rounded-full cursor-pointer transition duration-200 ${
              activeChip === chip 
                ? "bg-white text-black" 
                : "bg-zinc-800/80 text-white hover:bg-zinc-700"
            }`}
          >
            {chip}
          </button>
        ))}
      </div>

      {/* Grid: Getting Started Banner & Popular Albums */}
      <div className="grid grid-cols-1 xl:grid-cols-5 gap-6">
        
        {/* Getting started (2/5 columns) */}
        <div className="xl:col-span-2 flex flex-col gap-3">
          <h2 className="text-xl font-bold text-white tracking-tight">Getting started</h2>
          
          <div className="bg-gradient-to-br from-yellow-700/80 to-amber-950/90 rounded-lg p-5 flex flex-col justify-between min-h-[220px] md:h-[256px] border border-yellow-700/20 relative overflow-hidden group">
            {/* Background design */}
            <div className="absolute top-4 right-4 w-44 h-44 bg-yellow-500/10 rounded-full blur-2xl" />
            
            <div className="flex flex-col gap-2 relative">
              <h3 className="text-2xl font-extrabold text-white leading-tight">1. Start playing</h3>
              <p className="text-zinc-300 text-xs font-semibold leading-relaxed max-w-[220px]">
                Search, browse, and play your favorite artists and creators.
              </p>
            </div>
            
            <div className="flex items-center gap-4 mt-6 relative">
              <button className="bg-emerald-500 hover:bg-emerald-400 hover:scale-105 active:scale-95 text-black font-extrabold text-xs px-5 py-2.5 rounded-full transition cursor-pointer">
                Search
              </button>
              <span className="text-zinc-200 text-xs font-bold hover:underline cursor-pointer">
                Show more tips
              </span>
            </div>

            {/* Simulated playlist collage in card graphics */}
            <div className="absolute bottom-4 right-4 flex flex-col gap-1.5 rotate-6 translate-y-2 opacity-80 group-hover:scale-105 transition duration-500">
              <div className="bg-zinc-900/90 text-[10px] text-zinc-300 font-bold px-3 py-1 rounded shadow-lg border border-zinc-800">
                Serotonin
              </div>
              <div className="bg-zinc-950 text-[10px] text-emerald-400 font-bold px-3 py-1 rounded shadow-lg border border-zinc-800">
                good energy
              </div>
              <div className="bg-zinc-900/90 text-[10px] text-zinc-300 font-bold px-3 py-1 rounded shadow-lg border border-zinc-800">
                lofi beats
              </div>
            </div>
          </div>
        </div>

        {/* Popular albums and singles (3/5 columns) */}
        <div className="xl:col-span-3 flex flex-col gap-3">
          <div className="flex justify-between items-end">
            <h2 className="text-xl font-bold text-white tracking-tight">Popular albums and singles</h2>
            <span className="text-zinc-400 text-xs font-bold hover:underline cursor-pointer">Show all</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
            {popularAlbums.map((album, idx) => (
              <div
                key={idx}
                onClick={() => onPlayDemo(album.prompt)}
                className="bg-zinc-900/40 hover:bg-zinc-800/80 p-3.5 rounded-lg border border-zinc-900/60 cursor-pointer transition duration-300 group relative flex flex-col gap-3 min-w-0"
              >
                {/* Cover Art */}
                <div className="relative aspect-square w-full rounded overflow-hidden shadow-md">
                  <img
                    src={album.image}
                    alt={album.title}
                    className="object-cover w-full h-full"
                  />
                  {/* Floating Play Button */}
                  <div className="absolute bottom-2 right-2 bg-emerald-500 hover:bg-emerald-400 text-black p-3 rounded-full shadow-lg opacity-0 translate-y-2 group-hover:opacity-100 group-hover:translate-y-0 transition duration-300 transform active:scale-95">
                    <Play className="w-4 h-4 fill-black" />
                  </div>
                </div>
                {/* Details */}
                <div className="flex flex-col min-w-0">
                  <h4 className="text-white text-xs font-bold truncate">{album.title}</h4>
                  <p className="text-zinc-500 text-[10px] leading-relaxed truncate mt-1">{album.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recommended for you */}
      <div className="flex flex-col gap-3">
        <div className="flex justify-between items-end">
          <h2 className="text-xl font-bold text-white tracking-tight">Recommended for you</h2>
          <span className="text-zinc-400 text-xs font-bold hover:underline cursor-pointer">Show all</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-4">
          {recommendedPlaylists.map((pl, idx) => (
            <div
              key={idx}
              onClick={() => onPlayDemo(pl.prompt)}
              className="bg-zinc-900/40 hover:bg-zinc-800/80 p-3.5 rounded-lg border border-zinc-900/60 cursor-pointer transition duration-300 group relative flex flex-col gap-3 min-w-0"
            >
              {/* Cover Art */}
              <div className="relative aspect-square w-full rounded overflow-hidden shadow-md">
                <img
                  src={pl.image}
                  alt={pl.title}
                  className="object-cover w-full h-full"
                />
                {/* Floating Play Button */}
                <div className="absolute bottom-2 right-2 bg-emerald-500 hover:bg-emerald-400 text-black p-3 rounded-full shadow-lg opacity-0 translate-y-2 group-hover:opacity-100 group-hover:translate-y-0 transition duration-300 transform active:scale-95">
                  <Play className="w-4 h-4 fill-black" />
                </div>
              </div>
              {/* Details */}
              <div className="flex flex-col min-w-0">
                <h4 className="text-white text-xs font-bold truncate">{pl.title}</h4>
                <p className="text-zinc-500 text-[10px] leading-relaxed mt-1 break-words line-clamp-2">{pl.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer bar spacing */}
      <div className="h-10" />
    </div>
  );
}
