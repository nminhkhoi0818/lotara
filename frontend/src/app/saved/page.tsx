"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Bookmark, Calendar, ArrowRight, Plus } from "lucide-react";
import Link from "next/link";
import { userService, SaveTripResponse } from "@/services/user.service";
import { Loader2 } from "lucide-react";

export default function SavedTripsPage() {
  const router = useRouter();
  const [trips, setTrips] = useState<SaveTripResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTrips = async () => {
      try {
        const userId = localStorage.getItem("userId");
        if (!userId) {
          setLoading(false);
          return;
        }

        const savedTrips = await userService.getAllSavedTrips(userId);
        setTrips(savedTrips);
      } catch (err) {
        console.error("Failed to fetch saved trips:", err);
        setError("Failed to load saved trips");
      } finally {
        setLoading(false);
      }
    };

    fetchTrips();
  }, []);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const extractTripInfo = (trip: SaveTripResponse) => {
    const itinerary = trip.itinerary_data;
    const days = itinerary?.days?.length || itinerary?.totalDays;
    const cities =
      itinerary?.cities ||
      (itinerary?.days
        ?.map((day: { city?: string }) => day.city)
        .filter(Boolean) as string[]) ||
      [];
    const uniqueCities = [...new Set(cities)] as string[];
    return { days, cities: uniqueCities };
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <main className="flex-1 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="w-10 h-10 text-primary animate-spin" />
            <p className="text-muted-foreground">Loading your saved trips...</p>
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <main className="flex-1 flex items-center justify-center">
          <Card className="p-8 text-center">
            <p className="text-destructive mb-4">{error}</p>
            <Button onClick={() => window.location.reload()}>Try again</Button>
          </Card>
        </main>
      </div>
    );
  }

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
          {trips.length > 0 ? (
            <div className="grid md:grid-cols-2 gap-6">
              {trips.map((trip) => {
                const { days, cities } = extractTripInfo(trip);
                return (
                  <Card
                    key={trip.id}
                    className="p-6 md:p-8 rounded-2xl border-border/50 hover:border-primary/30 transition-all hover:shadow-lg cursor-pointer group"
                  >
                    <div className="flex flex-col gap-6 h-full">
                      <div>
                        <h3 className="text-xl md:text-2xl font-bold text-foreground mb-3 group-hover:text-primary transition-colors">
                          {trip.name}
                        </h3>

                        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-6">
                          <Calendar className="w-4 h-4" />
                          <span>Created {formatDate(trip.created_at)}</span>
                        </div>

                        {days && (
                          <div className="inline-block px-3 py-1 rounded-full bg-primary/10 text-sm font-medium text-primary mb-4">
                            {days} days
                          </div>
                        )}
                      </div>

                      {cities && cities.length > 0 && (
                        <div>
                          <p className="text-xs font-semibold text-muted-foreground mb-2 uppercase tracking-wide">
                            Cities
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {cities.map((city, j) => (
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

                      {trip.notes && (
                        <div>
                          <p className="text-xs font-semibold text-muted-foreground mb-2 uppercase tracking-wide">
                            Notes
                          </p>
                          <p className="text-sm text-muted-foreground line-clamp-2">
                            {trip.notes}
                          </p>
                        </div>
                      )}

                      <Button
                        className="mt-auto w-full gap-2 group"
                        onClick={() => router.push(`/saved/${trip.id}`)}
                      >
                        View trip
                        <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                      </Button>
                    </div>
                  </Card>
                );
              })}
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
