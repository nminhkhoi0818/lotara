"use client";
import "@/styles/loading-overlay.css";
import { useState, useEffect } from "react";

function LoadingOverlayQuote() {
  const quotes = [
    "Summoning your inner travel wizard... Abracadabra, adventure awaits!",
    "Brewing a potion of perfect destinations... Stirring in some magic!",
    "Consulting the travel gods for your epic journey...",
    "Hacking the matrix to find your dream vacation...",
    "Feeding the recommendation algorithm with your vibes...",
    "Whispering to the winds of wanderlust...",
    "Unleashing the travel beast within you...",
    "Plotting world domination... one destination at a time!",
    "Decoding your travel DNA...",
    "Time-traveling to curate your future trips...",
    "Convincing pixels to pack your bags...",
    "Negotiating with jet lag for a smooth ride...",
    "Bargaining with the universe for sunny skies...",
    "Teaching robots the art of vacation planning...",
  ];

  const [currentQuote, setCurrentQuote] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentQuote((prev) => (prev + 1) % quotes.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col justify-center items-center fixed inset-0 bg-primary/10 z-50">
      <div className="loader">
        <svg width="100" height="100" viewBox="0 0 100 100">
          <defs>
            <mask id="clipping">
              <polygon points="0,0 100,0 100,100 0,100" fill="black"></polygon>
              <polygon points="25,25 75,25 50,75" fill="white"></polygon>
              <polygon points="50,25 75,75 25,75" fill="white"></polygon>
              <polygon points="35,35 65,35 50,65" fill="white"></polygon>
              <polygon points="35,35 65,35 50,65" fill="white"></polygon>
              <polygon points="35,35 65,35 50,65" fill="white"></polygon>
              <polygon points="35,35 65,35 50,65" fill="white"></polygon>
            </mask>
          </defs>
        </svg>
        <div className="box"></div>
      </div>
      <div>
        <p className="mt-4 text-center text-sm text-gray-700">
          {quotes[currentQuote]}
        </p>
      </div>
    </div>
  );
}
export default LoadingOverlayQuote;
