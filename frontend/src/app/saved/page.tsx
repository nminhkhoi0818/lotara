"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Bookmark, Calendar, ArrowRight, Plus } from "lucide-react";
import Link from "next/link";

interface SavedTrip {
  name: string;
  date: string;
  days?: number;
  cities?: string[];
}

export default function SavedTripsPage() {
  const router = useRouter();
  const [trips, setTrips] = useState<SavedTrip[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem("savedTrips");
    if (stored) {
      try {
        setTrips(JSON.parse(stored));
      } catch {
        setTrips([]);
      }
    }
    setLoading(false);
  }, []);

  const sampleTrips: SavedTrip[] = [
    {
      name: "Summer 2026 Vietnam Adventure",
      date: "Jan 15, 2026",
      days: 11,
      cities: ["Hanoi", "Ha Long Bay", "Da Nang"],
    },
    {
      name: "Workcation Mode - Da Nang Focus",
      date: "Dec 20, 2025",
      days: 14,
      cities: ["Da Nang", "Hoi An"],
    },
  ];

  const allTrips = trips.length > 0 ? trips : sampleTrips;

  if (loading) return null;

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <main className="flex-1">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-24">
          {/* Header */}
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 mb-12">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-3 flex items-center gap-3">
                <Bookmark className="w-10 h-10 text-primary" />
                Your Saved Trips
              </h1>
              <p className="text-lg text-muted-foreground">
                Access and manage all your personalized itineraries
              </p>
            </div>

            <Link href="/onboarding">
              <Button size="lg" className="gap-2 px-8 h-12">
                <Plus className="w-5 h-5" />
                Create new trip
              </Button>
            </Link>
          </div>

          {/* Trips Grid */}
          {allTrips.length > 0 ? (
            <div className="grid md:grid-cols-2 gap-6">
              {allTrips.map((trip, i) => (
                <Card
                  key={i}
                  className="p-6 md:p-8 rounded-2xl border-border/50 hover:border-primary/30 transition-all hover:shadow-lg cursor-pointer group"
                >
                  <div className="flex flex-col gap-6 h-full">
                    <div>
                      <h3 className="text-xl md:text-2xl font-bold text-foreground mb-3 group-hover:text-primary transition-colors">
                        {trip.name}
                      </h3>

                      <div className="flex items-center gap-2 text-sm text-muted-foreground mb-6">
                        <Calendar className="w-4 h-4" />
                        <span>Created {trip.date}</span>
                      </div>

                      {trip.days && (
                        <div className="inline-block px-3 py-1 rounded-full bg-primary/10 text-sm font-medium text-primary mb-4">
                          {trip.days} days
                        </div>
                      )}
                    </div>

                    {trip.cities && (
                      <div>
                        <p className="text-xs font-semibold text-muted-foreground mb-2 uppercase tracking-wide">
                          Cities
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {trip.cities.map((city, j) => (
                            <span
                              key={j}
                              className="px-3 py-1 rounded-full bg-secondary/10 text-sm font-medium text-foreground"
                            >
                              {city}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    <Button
                      className="mt-auto w-full gap-2 group"
                      onClick={() => router.push("/result")}
                    >
                      View trip
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-12 md:p-16 rounded-2xl text-center border-border/50">
              <Bookmark className="w-16 h-16 text-muted-foreground/30 mx-auto mb-6" />
              <h2 className="text-2xl font-bold text-foreground mb-3">
                No saved trips yet
              </h2>
              <p className="text-muted-foreground mb-8 max-w-xl mx-auto">
                Create your first personalized Vietnam trip to get started
              </p>
              <Link href="/onboarding">
                <Button size="lg" className="px-8 h-12">
                  Create your first trip
                </Button>
              </Link>
            </Card>
          )}
        </div>
      </main>
    </div>
  );
}
