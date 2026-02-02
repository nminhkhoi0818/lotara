"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Sparkles,
  MapPin,
  Briefcase,
  Clock,
  Loader2,
  RotateCcw,
} from "lucide-react";
import { recommendService } from "@/services/recommend.service";
import { userService } from "@/services/user.service";
import LoadingOverlay from "@/components/loading-overlay";
import LoadingWave from "@/components/loading-wave";

interface PersonaAnswers {
  duration: string;
  companions: string;
  budget: string;
  pace: string;
  travelStyle: string;
  activity: string;
  crowds: string;
  accommodation: string;
  remote: boolean;
  timing: string;
}

export default function PersonaPage() {
  const router = useRouter();
  const [persona, setPersona] = useState<PersonaAnswers | null>(null);
  const [loading, setLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generateError, setGenerateError] = useState<string | null>(null);
  const [summary, setSummary] = useState("");
  const [displayedSummary, setDisplayedSummary] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  const handlePersonaSummary = async () => {
    try {
      const data = localStorage.getItem("onboardingAnswer");
      console.log("Onboarding data for persona summary:", data);
      setIsStreaming(true);
      setIsTyping(true);
      await userService.getPersonaSummary(
        data ? JSON.parse(data) : null,
        (event) => {
          if (event.type === "user") {
            localStorage.setItem("userId", event.data.userId);
          }
          if (event.type === "ai_chunk") {
            setSummary((prev) => prev + event.data);
          } else if (event.type === "complete") {
            setIsStreaming(false);
          } else if (event.type === "error") {
            console.error("Error:", event.data);
            setIsStreaming(false);
          }
        },
      );
    } catch (error) {
      console.error("Failed to fetch persona summary:", error);
      setIsStreaming(false);
    }
  };

  useEffect(() => {
    const stored = localStorage.getItem("personaAnswers");
    if (stored) {
      setPersona(JSON.parse(stored));
      setLoading(false);
      handlePersonaSummary();
    } else {
      router.push("/onboarding");
    }
  }, [router]);

  useEffect(() => {
    if (isTyping && summary && displayedSummary.length < summary.length) {
      const timer = setTimeout(() => {
        setDisplayedSummary(summary.slice(0, displayedSummary.length + 1));
      }, 20);
      return () => clearTimeout(timer);
    } else if (
      displayedSummary.length === summary.length &&
      summary.length > 0
    ) {
      setIsTyping(false);
    }
  }, [isTyping, summary, displayedSummary]);

  if (loading) return null;

  if (!persona) return null;

  const durationLabels: Record<string, string> = {
    short: "3-5 Days",
    medium: "1-2 Weeks",
    long: "2-4 Weeks",
    extended: "1 Month+",
  };

  const companionsLabels: Record<string, string> = {
    solo: "Solo Adventurer",
    couple: "Couple's Journey",
    family_kids: "Family with Kids",
    family_adults: "Adult Family Trip",
    friends: "Friends Group",
  };

  const budgetLabels: Record<string, string> = {
    budget: "Budget Traveler",
    midrange: "Mid-Range",
    comfortable: "Comfortable",
    luxury: "Luxury",
  };

  const paceLabels: Record<string, string> = {
    slow: "Slow & Deep",
    balanced: "Balanced Pace",
    fast: "Fast-Paced",
  };

  const styleLabels: Record<string, string> = {
    adventure: "Adventure Seeker",
    cultural: "Culture Enthusiast",
    nature: "Nature Lover",
    food: "Culinary Explorer",
    wellness: "Wellness Focused",
    photography: "Photography Enthusiast",
  };

  const activityLabels: Record<string, string> = {
    low: "Relaxed Pace",
    medium: "Moderately Active",
    high: "Very Active",
  };

  const crowdsLabels: Record<string, string> = {
    avoid: "Hidden Gems",
    mixed: "Balanced Mix",
    embrace: "Iconic Spots",
  };

  const accommodationLabels: Record<string, string> = {
    hostel: "Hostels & Guesthouses",
    standard: "Standard Hotels",
    boutique: "Boutique Hotels",
    premium: "Luxury Resorts",
  };

  const timingLabels: Record<string, string> = {
    morning: "Early Riser",
    flexible: "Flexible Schedule",
    evening: "Late Starter",
  };

  const handleGenerateTrip = async () => {
    const userId = localStorage.getItem("userId");
    if (!userId) {
      setGenerateError("User not found. Please complete onboarding again.");
      return;
    }

    setIsGenerating(true);
    setGenerateError(null);

    try {
      const recommendations = await recommendService.getRecommendations(userId);
      console.log("Received recommendations:", recommendations);
      localStorage.setItem("recommendations", JSON.stringify(recommendations));
      router.push("/result");
    } catch (error) {
      console.error("Failed to generate recommendations:", error);
      setGenerateError("Failed to generate your trip. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-linear-to-br from-background to-background">
      {isGenerating && <LoadingOverlay />}
      <main className="flex-1">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-block mb-6">
              <div className="w-16 h-16 rounded-full bg-linear-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                <Sparkles className="w-8 h-8 text-primary" />
              </div>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Your Travel Persona
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              {
                "Based on your preferences, here's your personalized Vietnam travel profile"
              }
            </p>
          </div>

          {/* AI-Generated Persona Summary */}
          <div className="mb-12">
            <Card className="p-8 md:p-10 rounded-3xl border-primary/30 bg-linear-to-br from-primary/5 via-secondary/5 to-accent/5 shadow-lg">
              <div className="flex items-start gap-4 mb-4">
                <div className="w-12 h-12 rounded-xl bg-primary/20 flex items-center justify-center shrink-0">
                  <Sparkles className="w-6 h-6 text-primary" />
                </div>
                <div className="flex-1">
                  <h2 className="text-xl font-bold text-foreground mb-1">
                    Your Personalized Travel Profile
                  </h2>
                  <p className="text-sm text-muted-foreground">
                    AI-generated insights based on your preferences
                  </p>
                </div>
              </div>
              {summary.length === 0 && <LoadingWave />}
              <p className="text-base md:text-lg leading-relaxed text-foreground/90">
                {displayedSummary}
                {summary.length !== 0 && (isStreaming || isTyping) && (
                  <span className="inline-block w-0.5 h-5 bg-primary ml-1 animate-pulse" />
                )}
              </p>
            </Card>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <Card className="p-4 rounded-xl border-primary/20 text-center">
              <p className="text-2xl font-bold text-primary mb-1">
                {durationLabels[persona.duration]}
              </p>
              <p className="text-xs text-muted-foreground uppercase">
                Duration
              </p>
            </Card>
            <Card className="p-4 rounded-xl border-primary/20 text-center">
              <p className="text-2xl font-bold text-secondary mb-1">
                {styleLabels[persona.travelStyle]}
              </p>
              <p className="text-xs text-muted-foreground uppercase">Style</p>
            </Card>
            <Card className="p-4 rounded-xl border-primary/20 text-center">
              <p className="text-2xl font-bold text-accent mb-1">
                {paceLabels[persona.pace]}
              </p>
              <p className="text-xs text-muted-foreground uppercase">Pace</p>
            </Card>
            <Card className="p-4 rounded-xl border-primary/20 text-center">
              <p className="text-2xl font-bold text-primary mb-1">
                {budgetLabels[persona.budget]}
              </p>
              <p className="text-xs text-muted-foreground uppercase">Budget</p>
            </Card>
          </div>

          {/* Detailed Preferences */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">
              Detailed Preferences
            </h3>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mb-12">
            {/* Travel Companions */}
            <Card className="p-4 rounded-xl border-border/50">
              <div className="flex items-center gap-2 mb-1">
                <MapPin className="w-4 h-4 text-muted-foreground" />
                <h3 className="text-xs font-medium text-muted-foreground">
                  Traveling With
                </h3>
              </div>
              <p className="text-sm font-semibold text-foreground">
                {companionsLabels[persona.companions]}
              </p>
            </Card>

            {/* Activity Level */}
            <Card className="p-4 rounded-xl border-border/50">
              <div className="flex items-center gap-2 mb-1">
                <Sparkles className="w-4 h-4 text-muted-foreground" />
                <h3 className="text-xs font-medium text-muted-foreground">
                  Activity Level
                </h3>
              </div>
              <p className="text-sm font-semibold text-foreground">
                {activityLabels[persona.activity]}
              </p>
            </Card>

            {/* Crowd Preference */}
            <Card className="p-4 rounded-xl border-border/50">
              <div className="flex items-center gap-2 mb-1">
                <MapPin className="w-4 h-4 text-muted-foreground" />
                <h3 className="text-xs font-medium text-muted-foreground">
                  Crowd Style
                </h3>
              </div>
              <p className="text-sm font-semibold text-foreground">
                {crowdsLabels[persona.crowds]}
              </p>
            </Card>

            {/* Accommodation */}
            <Card className="p-4 rounded-xl border-border/50">
              <div className="flex items-center gap-2 mb-1">
                <Sparkles className="w-4 h-4 text-muted-foreground" />
                <h3 className="text-xs font-medium text-muted-foreground">
                  Accommodation
                </h3>
              </div>
              <p className="text-sm font-semibold text-foreground">
                {accommodationLabels[persona.accommodation]}
              </p>
            </Card>

            {/* Work Mode */}
            <Card className="p-4 rounded-xl border-border/50">
              <div className="flex items-center gap-2 mb-1">
                <Briefcase className="w-4 h-4 text-muted-foreground" />
                <h3 className="text-xs font-medium text-muted-foreground">
                  Work Mode
                </h3>
              </div>
              <p className="text-sm font-semibold text-foreground">
                {persona.remote ? "Remote Work" : "Full Vacation"}
              </p>
            </Card>

            {/* Daily Rhythm */}
            <Card className="p-4 rounded-xl border-border/50">
              <div className="flex items-center gap-2 mb-1">
                <Clock className="w-4 h-4 text-muted-foreground" />
                <h3 className="text-xs font-medium text-muted-foreground">
                  Daily Rhythm
                </h3>
              </div>
              <p className="text-sm font-semibold text-foreground">
                {timingLabels[persona.timing]}
              </p>
            </Card>
          </div>

          {/* CTA */}
          <div className="bg-linear-to-br from-primary/5 to-secondary/5 rounded-3xl border border-primary/20 p-12 text-center">
            <h2 className="text-2xl md:text-3xl font-bold text-foreground mb-4">
              Ready for your personalized trip?
            </h2>
            <p className="text-muted-foreground mb-8 max-w-xl mx-auto">
              {
                "Based on your travel persona, we're generating the perfect Vietnam itinerary just for you"
              }
            </p>
            {generateError && (
              <div className="bg-destructive/10 border border-destructive/20 rounded-xl p-4 mb-6 max-w-xl mx-auto">
                <p className="text-sm text-destructive">{generateError}</p>
              </div>
            )}
            <div className="flex flex-col sm:flex-row gap-3 items-center justify-center">
              <Button
                size="lg"
                onClick={handleGenerateTrip}
                disabled={isGenerating}
                className="px-8 h-12 text-base gap-2"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Generating your trip...
                  </>
                ) : (
                  <>
                    Generate my trip
                    <Sparkles className="w-5 h-5" />
                  </>
                )}
              </Button>
              <Button
                size="lg"
                variant="outline"
                onClick={() => router.push("/onboarding")}
                className="px-8 h-12 text-base gap-2 border-2 hover:text-primary-foreground"
              >
                <RotateCcw className="w-5 h-5" />
                Create new persona
              </Button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
