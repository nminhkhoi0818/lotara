"use client";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Card } from "@/components/ui/card";
import { Brain, Zap, Layers, BarChart3 } from "lucide-react";

export default function ExplainPage() {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <main className="flex-1">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-24">
          {/* Header */}
          <div className="text-center mb-16">
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              How Lotara Works
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              {
                "Transparency is key. Here's exactly how our AI analyzed your answers to create your personalized trip"
              }
            </p>
          </div>

          {/* Main Accordion */}
          <div className="space-y-4 mb-12">
            <Accordion type="single" collapsible className="w-full space-y-3">
              <AccordionItem
                value="persona"
                className="border-b border-border/50"
              >
                <AccordionTrigger className="py-6">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                      <Brain className="w-5 h-5 text-primary" />
                    </div>
                    <div className="text-left">
                      <h3 className="font-semibold text-foreground">
                        Persona Extraction
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        How we built your travel profile
                      </p>
                    </div>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="pb-6">
                  <div className="space-y-4 pl-13">
                    <p className="text-muted-foreground">
                      We analyzed your 5 key answers to create a unique
                      personality profile:
                    </p>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li className="flex items-start gap-2">
                        <span className="text-primary font-bold">•</span>
                        <span>
                          Your budget level determines accommodation and dining
                          options
                        </span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-primary font-bold">•</span>
                        <span>
                          Remote work preferences shape the itinerary structure
                        </span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-primary font-bold">•</span>
                        <span>
                          Crowd tolerance influences destination and timing
                          choices
                        </span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-primary font-bold">•</span>
                        <span>
                          Travel style filters activities and experiences
                        </span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-primary font-bold">•</span>
                        <span>
                          Energy patterns optimize your daily schedule
                        </span>
                      </li>
                    </ul>
                  </div>
                </AccordionContent>
              </AccordionItem>

              <AccordionItem
                value="city-scoring"
                className="border-b border-border/50"
              >
                <AccordionTrigger className="py-6">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-secondary/10 flex items-center justify-center shrink-0">
                      <BarChart3 className="w-5 h-5 text-secondary" />
                    </div>
                    <div className="text-left">
                      <h3 className="font-semibold text-foreground">
                        City Scoring Logic
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {"How we ranked Vietnam's destinations"}
                      </p>
                    </div>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="pb-6">
                  <div className="space-y-4 pl-13">
                    <p className="text-muted-foreground">
                      Each city is evaluated on a 100-point scale considering:
                    </p>
                    <div className="space-y-3 text-sm">
                      <div className="bg-background p-4 rounded-lg border border-border/50">
                        <p className="font-semibold text-foreground mb-2">
                          Cultural Value (25 points)
                        </p>
                        <p className="text-muted-foreground">
                          How rich in culture and history compared to your
                          preferences
                        </p>
                      </div>
                      <div className="bg-background p-4 rounded-lg border border-border/50">
                        <p className="font-semibold text-foreground mb-2">
                          Budget Fit (25 points)
                        </p>
                        <p className="text-muted-foreground">
                          Average daily costs vs your stated budget range
                        </p>
                      </div>
                      <div className="bg-background p-4 rounded-lg border border-border/50">
                        <p className="font-semibold text-foreground mb-2">
                          Crowd Match (25 points)
                        </p>
                        <p className="text-muted-foreground">
                          How well the density matches your preference
                        </p>
                      </div>
                      <div className="bg-background p-4 rounded-lg border border-border/50">
                        <p className="font-semibold text-foreground mb-2">
                          Workation Ready (25 points)
                        </p>
                        <p className="text-muted-foreground">
                          WiFi quality, co-working spaces, and quiet hours
                        </p>
                      </div>
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>

              <AccordionItem
                value="hotel-filtering"
                className="border-b border-border/50"
              >
                <AccordionTrigger className="py-6">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center shrink-0">
                      <Zap className="w-5 h-5 text-accent" />
                    </div>
                    <div className="text-left">
                      <h3 className="font-semibold text-foreground">
                        Hotel Filtering Rules
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        How we selected accommodations
                      </p>
                    </div>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="pb-6">
                  <div className="space-y-4 pl-13">
                    <p className="text-muted-foreground">
                      Hotels are filtered using a multi-stage process:
                    </p>
                    <div className="space-y-3 text-sm">
                      <div className="bg-background p-4 rounded-lg border border-border/50">
                        <p className="font-semibold text-foreground mb-2">
                          Step 1: Budget Filter
                        </p>
                        <p className="text-muted-foreground">
                          Eliminate options outside your budget range (±15%)
                        </p>
                      </div>
                      <div className="bg-background p-4 rounded-lg border border-border/50">
                        <p className="font-semibold text-foreground mb-2">
                          Step 2: Work Requirements
                        </p>
                        <p className="text-muted-foreground">
                          For remote workers: WiFi ≥ 8/10, desk available, quiet
                          rooms
                        </p>
                      </div>
                      <div className="bg-background p-4 rounded-lg border border-border/50">
                        <p className="font-semibold text-foreground mb-2">
                          Step 3: Amenity Match
                        </p>
                        <p className="text-muted-foreground">
                          Match preferred amenities (gym, pool, spa, etc.)
                        </p>
                      </div>
                      <div className="bg-background p-4 rounded-lg border border-border/50">
                        <p className="font-semibold text-foreground mb-2">
                          Step 4: Ranking
                        </p>
                        <p className="text-muted-foreground">
                          Final scoring by guest satisfaction + noise level
                        </p>
                      </div>
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>

              <AccordionItem
                value="itinerary-agent"
                className="border-b border-border/50"
              >
                <AccordionTrigger className="py-6">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                      <Layers className="w-5 h-5 text-primary" />
                    </div>
                    <div className="text-left">
                      <h3 className="font-semibold text-foreground">
                        Itinerary Agent Flow
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        Decision hierarchy for daily activities
                      </p>
                    </div>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="pb-6">
                  <div className="space-y-4 pl-13">
                    <p className="text-muted-foreground">
                      The itinerary agent uses a decision tree to maximize
                      satisfaction:
                    </p>
                    <div className="space-y-3 text-sm">
                      <div className="bg-background p-4 rounded-lg border border-border/50">
                        <p className="font-semibold text-foreground mb-2">
                          1. Energy Alignment
                        </p>
                        <p className="text-muted-foreground">
                          Morning person? Outdoor activities early. Night owl?
                          Evening experiences.
                        </p>
                      </div>
                      <div className="bg-background p-4 rounded-lg border border-border/50">
                        <p className="font-semibold text-foreground mb-2">
                          2. Travel Style Matching
                        </p>
                        <p className="text-muted-foreground">
                          Weight activities toward your preferred travel style
                          (adventure, culture, food, etc.)
                        </p>
                      </div>
                      <div className="bg-background p-4 rounded-lg border border-border/50">
                        <p className="font-semibold text-foreground mb-2">
                          3. Work Integration
                        </p>
                        <p className="text-muted-foreground">
                          Insert 2-3 hour work blocks during low-energy periods
                        </p>
                      </div>
                      <div className="bg-background p-4 rounded-lg border border-border/50">
                        <p className="font-semibold text-foreground mb-2">
                          4. Pace Management
                        </p>
                        <p className="text-muted-foreground">
                          Balance activity with rest to prevent burnout
                        </p>
                      </div>
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>

          {/* Trust Section */}
          <Card className="p-8 md:p-12 rounded-2xl bg-linear-to-br from-primary/5 to-secondary/5 border-primary/20">
            <h2 className="text-2xl font-bold text-foreground mb-4">
              Our Commitment to Explainability
            </h2>
            <p className="text-muted-foreground mb-4">
              {
                " We believe in transparent AI. Every recommendation comes with a reason. You're never left wondering why we chose something—we show you the logic, the data, and the decision process."
              }
            </p>
            <p className="text-muted-foreground">
              {
                "Your feedback helps us improve. If something doesn't feel right, let us know and we'll adjust the scoring for future trips."
              }
            </p>
          </Card>
        </div>
      </main>
    </div>
  );
}
