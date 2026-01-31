/* eslint-disable @typescript-eslint/no-explicit-any */

"use client";

import { useState, useEffect } from "react";
// import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  BookmarkPlus,
  Share2,
  ChevronRight,
  Clock,
  MapPin,
  DollarSign,
} from "lucide-react";

export default function ResultPage() {
  // const router = useRouter();
  const [recommendations, setRecommendations] = useState<any>(null);
  const [saved, setSaved] = useState(false);
  const [activeTab, setActiveTab] = useState("itinerary");

  useEffect(() => {
    const stored = localStorage.getItem("recommendations");
    if (stored) {
      setRecommendations(JSON.parse(stored));
    }
  }, []);

  const handleSave = () => {
    setSaved(true);
    if (recommendations) {
      localStorage.setItem(
        "savedTrips",
        JSON.stringify([
          {
            name: recommendations.itinerary.trip_name,
            date: new Date().toLocaleDateString(),
          },
        ]),
      );
    }
  };

  if (!recommendations) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center mx-auto mb-4">
            <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
          </div>
          <p className="text-lg text-muted-foreground">Loading your trip...</p>
        </div>
      </div>
    );
  }

  const itinerary = recommendations.itinerary;
  const tripOverview = itinerary.trip_overview;

  // Extract hotels from itinerary
  const hotels = tripOverview
    .flatMap((day: any) =>
      day.events.filter((e: any) => e.event_type === "hotel_checkin"),
    )
    .map((event: any) => ({
      name: event.location.name,
      price: parseInt(event.budget.split(" ")[0].replace("$", "")) || 0,
      wifi: "Good",
      noise: "Quiet",
      why: event.description,
    }));

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <main className="flex-1">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">
          {/* Header */}
          <div className="mb-12">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 mb-8">
              <div>
                <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-3">
                  {itinerary.trip_name}
                </h1>
                <p className="text-lg text-muted-foreground max-w-2xl">
                  From {itinerary.start_date} to {itinerary.end_date} •{" "}
                  {itinerary.total_days} days
                </p>
              </div>

              <div className="flex gap-3 shrink-0">
                <Button
                  variant="outline"
                  size="lg"
                  onClick={handleSave}
                  disabled={saved}
                >
                  <BookmarkPlus className="w-5 h-5" />
                  {saved ? "Saved" : "Save Trip"}
                </Button>
                <Button variant="outline" size="lg">
                  <Share2 className="w-5 h-5" />
                </Button>
              </div>
            </div>

            {/* Trip Stats */}
            <div className="grid grid-cols-2 gap-4 md:gap-6">
              <div className="p-4 md:p-6 rounded-xl bg-primary/5 border border-primary/20">
                <p className="text-xs md:text-sm text-muted-foreground mb-2">
                  Total Days
                </p>
                <p className="text-2xl md:text-3xl font-bold text-foreground">
                  {itinerary.total_days} Days
                </p>
              </div>
              <div className="p-4 md:p-6 rounded-xl bg-secondary/5 border border-secondary/20">
                <p className="text-xs md:text-sm text-muted-foreground mb-2">
                  Average Daily Budget
                </p>
                <p className="text-2xl md:text-3xl font-bold text-foreground">
                  {itinerary.average_budget_spend_per_day}
                </p>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <Tabs
            value={activeTab}
            onValueChange={setActiveTab}
            className="mb-12"
          >
            <TabsList className="grid w-full md:w-auto grid-cols-2 mb-8">
              <TabsTrigger value="itinerary">Itinerary</TabsTrigger>
              <TabsTrigger value="hotels">Hotels</TabsTrigger>
            </TabsList>

            {/* Hotels Tab */}
            <TabsContent value="hotels" className="space-y-4">
              {hotels.map((hotel: any, i: any) => (
                <Card
                  key={i}
                  className="p-6 md:p-8 rounded-2xl border-border/50 hover:border-primary/30 transition-colors"
                >
                  <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                    <div className="flex-1">
                      <h3 className="text-xl md:text-2xl font-bold text-foreground mb-3">
                        {hotel.name}
                      </h3>
                      <p className="text-muted-foreground mb-4">{hotel.why}</p>
                      <div className="grid grid-cols-3 gap-4">
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">
                            Per Night
                          </p>
                          <p className="font-semibold text-foreground">
                            ${hotel.price}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">
                            WiFi Quality
                          </p>
                          <p className="font-semibold text-foreground">
                            {hotel.wifi}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">
                            Noise Level
                          </p>
                          <p className="font-semibold text-foreground">
                            {hotel.noise}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </TabsContent>

            {/* Itinerary Tab */}
            <TabsContent value="itinerary" className="space-y-6">
              {tripOverview.map((day: any, i: any) => (
                <Card
                  key={i}
                  className="p-6 md:p-8 rounded-2xl border-border/50"
                >
                  <div className="mb-6">
                    <h3 className="text-xl md:text-2xl font-bold text-foreground mb-2">
                      Day {day.trip_number}:{" "}
                      {new Date(day.start_date).toLocaleDateString("en-US", {
                        weekday: "long",
                        month: "long",
                        day: "numeric",
                      })}
                    </h3>
                    <p className="text-muted-foreground">{day.summary}</p>
                  </div>
                  <div className="space-y-4">
                    {day.events.map((event: any, j: any) => (
                      <div
                        key={j}
                        className="flex gap-4 p-4 rounded-lg bg-muted/30 border border-border/30"
                      >
                        {event.image_url && (
                          <div className="w-16 h-16 rounded-lg overflow-hidden shrink-0">
                            <img
                              src={event.image_url}
                              alt={event.description}
                              className="w-full h-full object-cover"
                            />
                          </div>
                        )}
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <Clock className="w-4 h-4 text-muted-foreground" />
                            <span className="text-sm font-medium text-foreground">
                              {event.start_time} - {event.end_time}
                            </span>
                          </div>
                          <h4 className="font-semibold text-foreground mb-1">
                            {event.description}
                          </h4>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <MapPin className="w-4 h-4" />
                              <span>{event.location.name}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <DollarSign className="w-4 h-4" />
                              <span>{event.budget}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              ))}
            </TabsContent>
          </Tabs>

          {/* Bottom CTA */}
          <div className="flex flex-col md:flex-row gap-4 items-center justify-center">
            <Link href="/explain">
              <Button
                variant="outline"
                size="lg"
                className="w-full md:w-auto bg-transparent"
              >
                Understand the AI reasoning
              </Button>
            </Link>
            <Link href="/">
              <Button size="lg" className="w-full md:w-auto">
                Start another trip
              </Button>
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
