"use client";

import { useState } from "react";
// import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BookmarkPlus, Share2, ChevronRight } from "lucide-react";

const cities = [
  {
    name: "Hanoi",
    why: "Perfect blend of history, culture, and vibrant street food scene. Ideal for cultural explorers with morning-person energy.",
    budget: "$$",
    crowd: "High",
    days: 3,
  },
  {
    name: "Ha Long Bay",
    why: "Stunning natural wonder offering relaxation and adventure. Great for photography and peaceful moments.",
    budget: "$",
    crowd: "Medium",
    days: 2,
  },
  {
    name: "Da Nang",
    why: "Perfect workcation hub with great cafes, beaches, and reliable WiFi. Balance work and exploration seamlessly.",
    budget: "$$",
    crowd: "Low-Medium",
    days: 3,
  },
];

const hotels = [
  {
    name: "Heritage Charm Hotel",
    price: 45,
    wifi: "Excellent",
    noise: "Quiet",
    why: "Central location with traditional architecture. Budget-friendly with character.",
  },
  {
    name: "Modern Workspace Stay",
    price: 75,
    wifi: "Premium",
    noise: "Quiet",
    why: "Dedicated co-working space. Perfect for remote workers needing productivity.",
  },
  {
    name: "Beachfront Wellness Resort",
    price: 120,
    wifi: "Good",
    noise: "Very Quiet",
    why: "Spa and wellness facilities. Best for relaxation-focused travelers.",
  },
  {
    name: "Cultural Guesthouse",
    price: 35,
    wifi: "Good",
    noise: "Moderate",
    why: "Run by locals offering authentic experiences and insider tips.",
  },
];

const itinerary = [
  {
    time: "Morning",
    activities: [
      "Sunrise at Hoan Kiem Lake",
      "Local coffee at traditional cafes",
      "Visit Ho Chi Minh Mausoleum",
    ],
  },
  {
    time: "Afternoon",
    activities: [
      "Street food tour in Old Quarter",
      "Temple exploration",
      "Work block - 2-3 hours",
    ],
  },
  {
    time: "Evening",
    activities: [
      "Sunset cruise on Red River",
      "Traditional water puppet show",
      "Dinner at rooftop restaurant",
    ],
  },
  {
    time: "Night",
    activities: [
      "Explore night markets",
      "Evening walk along illuminated streets",
      "Relax at local tea house",
    ],
  },
];

export default function ResultPage() {
  // const router = useRouter();
  const [saved, setSaved] = useState(false);
  const [activeTab, setActiveTab] = useState("cities");

  const handleSave = () => {
    setSaved(true);
    localStorage.setItem(
      "savedTrips",
      JSON.stringify([
        { name: "My Vietnam Trip", date: new Date().toLocaleDateString() },
      ]),
    );
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <main className="flex-1">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">
          {/* Header */}
          <div className="mb-12">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 mb-8">
              <div>
                <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-3">
                  Your Personalized Vietnam Trip
                </h1>
                <p className="text-lg text-muted-foreground max-w-2xl">
                  A 11-day journey tailored to your personality, budget, and
                  travel style
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
            <div className="grid grid-cols-3 gap-4 md:gap-6">
              <div className="p-4 md:p-6 rounded-xl bg-primary/5 border border-primary/20">
                <p className="text-xs md:text-sm text-muted-foreground mb-2">
                  Total Days
                </p>
                <p className="text-2xl md:text-3xl font-bold text-foreground">
                  11 Days
                </p>
              </div>
              <div className="p-4 md:p-6 rounded-xl bg-secondary/5 border border-secondary/20">
                <p className="text-xs md:text-sm text-muted-foreground mb-2">
                  Estimated Budget
                </p>
                <p className="text-2xl md:text-3xl font-bold text-foreground">
                  $850-1200
                </p>
              </div>
              <div className="p-4 md:p-6 rounded-xl bg-accent/5 border border-accent/20">
                <p className="text-xs md:text-sm text-muted-foreground mb-2">
                  Cities
                </p>
                <p className="text-2xl md:text-3xl font-bold text-foreground">
                  3 Cities
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
            <TabsList className="grid w-full md:w-auto grid-cols-3 mb-8">
              <TabsTrigger value="cities">Cities</TabsTrigger>
              <TabsTrigger value="hotels">Hotels</TabsTrigger>
              <TabsTrigger value="itinerary">Itinerary</TabsTrigger>
            </TabsList>

            {/* Cities Tab */}
            <TabsContent value="cities" className="space-y-4">
              {cities.map((city, i) => (
                <Card
                  key={i}
                  className="p-6 md:p-8 rounded-2xl border-border/50 hover:border-primary/30 transition-colors"
                >
                  <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 mb-6">
                    <div>
                      <h3 className="text-2xl md:text-3xl font-bold text-foreground mb-2 flex items-center gap-3">
                        <span className="text-3xl md:text-4xl">📍</span>
                        {city.name}
                      </h3>
                      <p className="text-muted-foreground">{city.why}</p>
                    </div>
                    <div className="flex gap-4 shrink-0">
                      <div className="text-right">
                        <p className="text-xs text-muted-foreground mb-1">
                          Budget Level
                        </p>
                        <p className="text-xl font-bold text-foreground">
                          {city.budget}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-muted-foreground mb-1">
                          Crowds
                        </p>
                        <p className="text-xl font-bold text-foreground">
                          {city.crowd}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-muted-foreground mb-1">
                          Days
                        </p>
                        <p className="text-xl font-bold text-foreground">
                          {city.days}
                        </p>
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </TabsContent>

            {/* Hotels Tab */}
            <TabsContent value="hotels" className="space-y-4">
              {hotels.map((hotel, i) => (
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
            <TabsContent value="itinerary" className="space-y-4">
              {itinerary.map((period, i) => (
                <Card
                  key={i}
                  className="p-6 md:p-8 rounded-2xl border-border/50"
                >
                  <h3 className="text-xl md:text-2xl font-bold text-foreground mb-4">
                    {period.time}
                  </h3>
                  <ul className="space-y-2">
                    {period.activities.map((activity, j) => (
                      <li
                        key={j}
                        className="flex items-start gap-3 text-muted-foreground"
                      >
                        <ChevronRight className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                        <span>{activity}</span>
                      </li>
                    ))}
                  </ul>
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
