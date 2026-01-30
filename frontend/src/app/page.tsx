"use client";

import Link from "next/link";
import Image from "next/image";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  ArrowRight,
  Sparkles,
  MapPin,
  Briefcase,
  Brain,
  BarChart3,
  CheckCircle2,
  Zap,
  Globe,
  Heart,
} from "lucide-react";

export default function Home() {
  const [hoveredFeature, setHoveredFeature] = useState<number | null>(null);

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <main className="flex-1">
        <section className="relative min-h-screen flex items-center overflow-hidden pt-20">
          {/* Animated background elements */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute -top-64 right-1/4 w-96 h-96 bg-primary/25 rounded-full blur-3xl" />
            <div className="absolute top-1/2 -left-32 w-96 h-96 bg-secondary/15 rounded-full blur-3xl" />
            <div className="absolute -bottom-48 right-1/3 w-80 h-80 bg-accent/10 rounded-full blur-3xl" />
            {/* Transition blobs */}
            <div className="absolute bottom-0 left-1/4 w-150 h-150 bg-primary/8 rounded-full blur-3xl" />
            <div className="absolute bottom-20 right-1/3 w-125 h-125 bg-secondary/6 rounded-full blur-3xl" />
          </div>

          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative z-10 w-full">
            <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
              {/* Left content */}
              <div className="flex flex-col gap-8 max-w-xl">
                <div className="space-y-6">
                  <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 w-fit">
                    <Sparkles className="w-4 h-4 text-primary" />
                    <span className="text-sm font-semibold text-primary">
                      AI Travel Planning Meets Personality
                    </span>
                  </div>

                  <h1 className="text-5xl lg:text-7xl font-bold text-foreground leading-tight text-balance tracking-tight">
                    Your Perfect Vietnam Trip, Designed for{" "}
                    <span className="text-primary">You</span>
                  </h1>

                  <p className="text-lg text-muted-foreground leading-relaxed">
                    Stop settling for generic recommendations. Lotara
                    understands your personality, work style, and travel dreams
                    to craft the perfect itinerary just for you.
                  </p>
                </div>

                {/* CTA buttons */}
                <div className="flex flex-col sm:flex-row gap-3 pt-4">
                  <Link href="/onboarding" className="flex-1 sm:flex-none">
                    <Button
                      size="lg"
                      className="w-full sm:w-auto gap-2 px-8 h-14 text-base font-semibold group shadow-lg hover:shadow-xl transition-shadow"
                    >
                      Start Planning Free
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </Button>
                  </Link>
                  <button className="px-8 h-14 rounded-xl border-2 border-border text-foreground font-semibold hover:bg-accent/5 hover:border-primary/30 transition-all flex items-center justify-center gap-2">
                    <Globe className="w-4 h-4" />
                    See Demo
                  </button>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4 pt-8 border-t border-border/30">
                  <div>
                    <p className="text-2xl font-bold text-foreground">2,000+</p>
                    <p className="text-sm text-muted-foreground">
                      Happy travelers
                    </p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-foreground">5 min</p>
                    <p className="text-sm text-muted-foreground">
                      To plan your trip
                    </p>
                  </div>
                </div>
              </div>

              {/* Right side - Visual showcase with floating cards */}
              <div className="relative hidden lg:block">
                <div className="relative h-96 flex items-center justify-center">
                  {/* Main logo card */}
                  <div className="absolute inset-0 bg-linear-to-br from-primary/10 via-secondary/5 to-transparent rounded-3xl border border-primary/20 backdrop-blur-sm overflow-hidden shadow-2xl">
                    <Image
                      src="/logo_icon.png"
                      alt="Lotara Logo"
                      width={280}
                      height={280}
                      className="absolute inset-0 w-full h-full object-contain p-8"
                    />
                  </div>

                  {/* Floating stat cards */}
                  <div
                    className="absolute -top-12 -left-8 bg-white dark:bg-gray-900 rounded-2xl p-4 shadow-xl border border-border/50 backdrop-blur-sm animate-bounce"
                    style={{ animationDelay: "0s" }}
                  >
                    <p className="text-2xl font-bold text-foreground">
                      AI-Powered
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Personalized
                    </p>
                  </div>

                  <div
                    className="absolute -bottom-8 -right-12 bg-white dark:bg-gray-900 rounded-2xl p-4 shadow-xl border border-border/50 backdrop-blur-sm animate-bounce"
                    style={{ animationDelay: "0.3s" }}
                  >
                    <p className="text-2xl font-bold text-secondary">Vietnam</p>
                    <p className="text-xs text-muted-foreground">Awaits You</p>
                  </div>

                  <div
                    className="absolute top-1/2 -right-4 bg-white dark:bg-gray-900 rounded-2xl p-4 shadow-xl border border-border/50 backdrop-blur-sm animate-bounce"
                    style={{ animationDelay: "0.6s" }}
                  >
                    <div className="flex items-center gap-2">
                      <Heart className="w-5 h-5 text-primary" />
                      <p className="text-sm font-semibold text-foreground">
                        Perfect Match
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="py-24 md:py-32 relative">
          {/* Smooth blob transitions */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute top-0 left-1/3 w-175 h-175 bg-primary/8 rounded-full blur-3xl" />
            <div className="absolute top-40 right-1/4 w-125 h-125 bg-secondary/6 rounded-full blur-3xl" />
            <div className="absolute bottom-0 left-1/2 w-150 h-150 bg-accent/5 rounded-full blur-3xl" />
          </div>
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
            <div className="text-center mb-20">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-secondary/10 border border-secondary/20 mb-6">
                <Zap className="w-4 h-4 text-secondary" />
                <span className="text-sm font-semibold text-secondary">
                  How It Works
                </span>
              </div>
              <h2 className="text-5xl lg:text-6xl font-bold text-foreground mb-6 text-balance">
                Three Steps to Your Dream Trip
              </h2>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Fast, personalized, and built just for you
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8 relative">
              {/* Connecting line */}
              <div className="hidden md:block absolute top-32 left-0 right-0 h-1 bg-linear-to-r from-primary/20 via-primary/40 to-primary/20" />

              {[
                {
                  step: 1,
                  title: "Answer Your Profile",
                  description:
                    "Chat with our AI to tell us about your travel style, budget, and preferences in just 5 minutes",
                  icon: Brain,
                  color: "from-primary to-secondary",
                },
                {
                  step: 2,
                  title: "Get Your Persona",
                  description:
                    "Discover your unique travel personality and see how it shapes your perfect trip",
                  icon: Sparkles,
                  color: "from-secondary to-accent",
                },
                {
                  step: 3,
                  title: "Receive Your Trip",
                  description:
                    "AI-curated cities, hand-picked hotels, and detailed itineraries tailored to you",
                  icon: MapPin,
                  color: "from-accent to-primary",
                },
              ].map((item) => {
                const Icon = item.icon;
                return (
                  <div key={item.step} className="relative group">
                    <div className="h-full flex flex-col gap-6 p-8 rounded-2xl border border-border/50 bg-card hover:border-primary/40 hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
                      <div className="relative">
                        <div
                          className={`w-16 h-16 rounded-2xl bg-linear-to-br ${item.color} flex items-center justify-center shadow-lg`}
                        >
                          <Icon className="w-8 h-8 text-white" />
                        </div>
                        <span className="absolute -bottom-3 -right-3 w-10 h-10 rounded-full bg-foreground text-background font-bold flex items-center justify-center text-sm">
                          {item.step}
                        </span>
                      </div>
                      <div>
                        <h3 className="text-2xl font-bold text-foreground mb-3">
                          {item.title}
                        </h3>
                        <p className="text-muted-foreground leading-relaxed">
                          {item.description}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        <section className="py-24 md:py-32 bg-linear-to-b from-primary/5 via-secondary/3 to-background">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-20">
              <h2 className="text-5xl lg:text-6xl font-bold text-foreground mb-6 text-balance">
                Why Travelers Love Lotara
              </h2>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Built with everything you need for an unforgettable Vietnam
                experience
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
              {[
                {
                  icon: Brain,
                  title: "Personality-Based Planning",
                  description:
                    "Your trip reflects your unique travel personality, not generic algorithms",
                  isHighlight: true,
                },
                {
                  icon: Briefcase,
                  title: "Workcation Mode",
                  description:
                    "Seamlessly blend work and travel with schedules that respect your deadlines",
                  isHighlight: false,
                },
                {
                  icon: MapPin,
                  title: "Budget-Smart Matching",
                  description:
                    "Perfect hotels within your budget with transparent pricing—no surprises",
                  isHighlight: true,
                },
                {
                  icon: BarChart3,
                  title: "Explainable AI",
                  description:
                    "Understand exactly why each recommendation was chosen for you with full transparency",
                  isHighlight: false,
                },
              ].map((feature, i) => {
                const Icon = feature.icon;
                return (
                  <div
                    key={i}
                    onMouseEnter={() => setHoveredFeature(i)}
                    onMouseLeave={() => setHoveredFeature(null)}
                    className={`p-8 rounded-2xl border transition-all duration-300 cursor-pointer ${
                      feature.isHighlight
                        ? "bg-linear-to-br from-primary/10 to-secondary/5 border-primary/30 hover:border-primary/60 hover:shadow-xl"
                        : "bg-card border-border/50 hover:border-primary/30 hover:shadow-lg hover:bg-linear-to-br hover:from-primary/5 hover:to-secondary/2"
                    } ${hoveredFeature === i ? "scale-105" : ""}`}
                  >
                    <div className="flex items-start gap-5">
                      <div
                        className={`w-14 h-14 rounded-xl flex items-center justify-center shrink-0 transition-all ${
                          feature.isHighlight
                            ? "bg-linear-to-br from-primary to-secondary text-white shadow-lg"
                            : "bg-primary/15 text-primary group-hover:bg-primary/25"
                        }`}
                      >
                        <Icon className="w-7 h-7" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-bold text-foreground mb-2 text-lg">
                          {feature.title}
                        </h3>
                        <p className="text-muted-foreground text-sm leading-relaxed">
                          {feature.description}
                        </p>
                        {feature.isHighlight && (
                          <div className="flex items-center gap-2 mt-4 pt-4 border-t border-primary/20">
                            <CheckCircle2 className="w-4 h-4 text-primary shrink-0" />
                            <span className="text-xs font-semibold text-primary">
                              Unique to Lotara
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        <section className="py-24 md:py-32 relative overflow-hidden bg-linear-to-b from-background via-primary/3 to-secondary/5">
          <div className="absolute inset-0 bg-linear-to-br from-primary/5 via-transparent to-secondary/5 opacity-50" />

          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
            <div className="relative overflow-hidden rounded-3xl border border-primary/20 backdrop-blur-xl bg-linear-to-br from-primary/5 via-secondary/5 to-transparent p-12 md:p-16 shadow-2xl">
              <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary/20 rounded-full blur-3xl" />
              <div className="absolute -bottom-32 -left-32 w-72 h-72 bg-secondary/15 rounded-full blur-3xl" />

              <div className="relative z-10 text-center">
                <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-6 text-balance">
                  Ready to Plan Your Dream Vietnam Trip?
                </h2>
                <p className="text-lg text-muted-foreground mb-10 max-w-2xl mx-auto leading-relaxed">
                  Join thousands of travelers discovering personalized
                  itineraries. Get started in 5 minutes with absolutely no
                  credit card required.
                </p>

                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Link href="/onboarding">
                    <Button
                      size="lg"
                      className="px-10 h-14 text-base font-semibold shadow-lg hover:shadow-xl transition-shadow"
                    >
                      Start Free Planning
                    </Button>
                  </Link>
                  <button className="px-10 h-14 rounded-xl border-2 border-primary/30 text-foreground font-semibold hover:bg-primary/10 transition-all backdrop-blur">
                    Schedule a Demo
                  </button>
                </div>

                <p className="text-sm text-muted-foreground mt-10 flex items-center justify-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-primary" />
                  No credit card required • Free trial • 100% personalized
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
