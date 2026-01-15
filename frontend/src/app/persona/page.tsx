"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Sparkles, MapPin, Briefcase, Clock } from "lucide-react";

interface PersonaAnswers {
  budget: string;
  remote: boolean;
  crowds: boolean;
  travelStyle: string;
  timing: string;
}

export default function PersonaPage() {
  const router = useRouter();
  const [persona, setPersona] = useState<PersonaAnswers | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem("personaAnswers");
    if (stored) {
      setPersona(JSON.parse(stored));
      setLoading(false);
    } else {
      router.push("/onboarding");
    }
  }, [router]);

  if (loading) return null;

  if (!persona) return null;

  const budgetLabels: Record<string, string> = {
    budget: "Budget Conscious",
    moderate: "Moderate",
    comfortable: "Comfortable",
    luxury: "Luxury",
  };

  const styleLabels: Record<string, string> = {
    adventure: "Adventure Seeker",
    cultural: "Culture Enthusiast",
    relaxation: "Wellness Focus",
    food: "Culinary Explorer",
  };

  const timingLabels: Record<string, string> = {
    early: "Early Bird",
    balanced: "Balanced",
    night: "Night Owl",
  };

  return (
    <div className="min-h-screen flex flex-col bg-linear-to-br from-background to-background">
      <main className="flex-1">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
          {/* Header */}
          <div className="text-center mb-16">
            <div className="inline-block mb-6">
              <div className="w-16 h-16 rounded-full bg-linear-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                <Sparkles className="w-8 h-8 text-primary" />
              </div>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Your Travel Persona
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              {" Based on your answers, here's your unique travel profile"}
            </p>
          </div>

          {/* Persona Cards Grid */}
          <div className="grid md:grid-cols-2 gap-6 mb-12">
            {/* Budget */}
            <Card className="p-8 rounded-2xl border-primary/20 hover:border-primary/40 transition-colors">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                  <MapPin className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-muted-foreground">
                    Travel Budget
                  </h3>
                  <p className="text-2xl font-bold text-foreground">
                    {budgetLabels[persona.budget]}
                  </p>
                </div>
              </div>
              <p className="text-sm text-muted-foreground">
                {persona.budget === "budget" &&
                  "Seeking affordable experiences and local gems"}
                {persona.budget === "moderate" &&
                  "Looking for good value and balanced comfort"}
                {persona.budget === "comfortable" &&
                  "Preferring quality accommodations and dining"}
                {persona.budget === "luxury" &&
                  "Seeking premium experiences and exclusive access"}
              </p>
            </Card>

            {/* Work Style */}
            <Card className="p-8 rounded-2xl border-primary/20 hover:border-primary/40 transition-colors">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 rounded-lg bg-secondary/10 flex items-center justify-center">
                  <Briefcase className="w-6 h-6 text-secondary" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-muted-foreground">
                    Work Style
                  </h3>
                  <p className="text-2xl font-bold text-foreground">
                    {persona.remote ? "Remote Worker" : "Full Vacation"}
                  </p>
                </div>
              </div>
              <p className="text-sm text-muted-foreground">
                {persona.remote
                  ? "Your itinerary includes work-friendly accommodations and schedules"
                  : "Your trip is optimized for complete relaxation and exploration"}
              </p>
            </Card>

            {/* Travel Vibe */}
            <Card className="p-8 rounded-2xl border-primary/20 hover:border-primary/40 transition-colors">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center">
                  <Sparkles className="w-6 h-6 text-accent" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-muted-foreground">
                    Travel Style
                  </h3>
                  <p className="text-2xl font-bold text-foreground">
                    {styleLabels[persona.travelStyle]}
                  </p>
                </div>
              </div>
              <p className="text-sm text-muted-foreground">
                {persona.travelStyle === "adventure" &&
                  "Seeking thrilling outdoor activities and natural wonders"}
                {persona.travelStyle === "cultural" &&
                  "Diving deep into local culture and historical sites"}
                {persona.travelStyle === "relaxation" &&
                  "Focusing on wellness, spas, and peaceful retreats"}
                {persona.travelStyle === "food" &&
                  "Exploring local cuisine and food markets"}
              </p>
            </Card>

            {/* Energy Pattern */}
            <Card className="p-8 rounded-2xl border-primary/20 hover:border-primary/40 transition-colors">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Clock className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-muted-foreground">
                    Energy Pattern
                  </h3>
                  <p className="text-2xl font-bold text-foreground">
                    {timingLabels[persona.timing]}
                  </p>
                </div>
              </div>
              <p className="text-sm text-muted-foreground">
                {persona.timing === "early" &&
                  "Your activities are scheduled for mornings and early afternoons"}
                {persona.timing === "balanced" &&
                  "Your itinerary is balanced throughout the day"}
                {persona.timing === "night" &&
                  "Your activities emphasize evenings and night experiences"}
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
            <Button
              size="lg"
              onClick={() => router.push("/result")}
              className="px-8 h-12 text-base gap-2"
            >
              Generate my trip
              <Sparkles className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
}
