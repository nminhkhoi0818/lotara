"use client";
import "@/styles/loading-overlay.css";
import { useState, useEffect } from "react";

function LoadingOverlayQuote() {
  const processingSteps = [
    "Analyzing your preferences...",
    "Searching destinations database...",
    "Matching with your travel style...",
    "Filtering by budget and dates...",
    "Evaluating weather conditions...",
    "Checking travel restrictions...",
    "Comparing prices and reviews...",
    "Generating personalized recommendations...",
  ];

  const MAX_VISIBLE = 4;

  useEffect(() => {
    // Lock scroll when overlay is shown
    document.body.style.overflow = "hidden";

    // Cleanup: restore scroll when component unmounts
    return () => {
      document.body.style.overflow = "";
    };
  }, []);

  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);

  useEffect(() => {
    const timeouts: NodeJS.Timeout[] = [];

    // Show steps sequentially
    processingSteps.forEach((_, index) => {
      const showTimeout = setTimeout(() => {
        setCurrentStepIndex(index + 1);

        // Mark as completed after a delay (except the last one)
        if (index < processingSteps.length - 1) {
          const completeTimeout = setTimeout(() => {
            setCompletedSteps((prev) => {
              if (prev.includes(index)) return prev;
              return [...prev, index];
            });
          }, 1500);
          timeouts.push(completeTimeout);
        }
      }, index * 2000);
      timeouts.push(showTimeout);
    });

    return () => {
      timeouts.forEach((timeout) => clearTimeout(timeout));
    };
  }, []);

  // Calculate which steps to show (last 4)
  const startIndex = Math.max(0, currentStepIndex - MAX_VISIBLE);
  const visibleSteps = Array.from(
    { length: Math.min(currentStepIndex, MAX_VISIBLE) },
    (_, i) => startIndex + i,
  );

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

      <div className="mt-8 max-w-md w-full px-8 pl-16">
        <div className="space-y-3 relative">
          {visibleSteps.map((stepIndex, arrayIndex) => {
            const isOldest =
              arrayIndex === 0 && visibleSteps.length === MAX_VISIBLE;
            const opacity = isOldest ? "opacity-30 blur-[1px]" : "opacity-100";

            return (
              <div
                key={`step-${stepIndex}`}
                className={`flex items-center gap-3 animate-in fade-in slide-in-from-left-2 duration-500 transition-all ${opacity}`}
              >
                <p className="text-sm text-gray-700 font-medium">
                  {processingSteps[stepIndex]}
                </p>
                {completedSteps.includes(stepIndex) ? (
                  <div className="flex-shrink-0 w-5 h-5 rounded-full bg-green-500 flex items-center justify-center">
                    <svg
                      className="w-3 h-3 text-white"
                      fill="none"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path d="M5 13l4 4L19 7"></path>
                    </svg>
                  </div>
                ) : (
                  <div className="flex-shrink-0 w-5 h-5 rounded-full border-2 border-blue-500 border-t-transparent animate-spin"></div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
export default LoadingOverlayQuote;
