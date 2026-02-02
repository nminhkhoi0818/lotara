/* eslint-disable @typescript-eslint/no-explicit-any */

"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Clock,
  MapPin,
  DollarSign,
  Trash2,
  ArrowLeft,
  Loader2,
} from "lucide-react";
import { userService, SaveTripResponse } from "@/services/user.service";
import { toast } from "sonner";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

export default function SavedTripDetailPage() {
  const params = useParams();
  const router = useRouter();
  const tripId = params.id as string;

  const [trip, setTrip] = useState<SaveTripResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("itinerary");
  const [deleting, setDeleting] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  useEffect(() => {
    const fetchTrip = async () => {
      try {
        const userId = localStorage.getItem("userId");
        if (!userId) {
          setError("User not found");
          setLoading(false);
          return;
        }

        const tripData = await userService.getSavedTripById(userId, tripId);
        setTrip(tripData);
      } catch (err) {
        console.error("Failed to fetch trip:", err);
        setError("Failed to load trip details");
      } finally {
        setLoading(false);
      }
    };

    if (tripId) {
      fetchTrip();
    }
  }, [tripId]);

  const handleDelete = async () => {
    if (!trip) return;

    setDeleting(true);
    try {
      const userId = localStorage.getItem("userId");
      if (!userId) {
        toast.error("User not found");
        return;
      }

      await userService.deleteSavedTrip(userId, trip.id);
      toast.success("Trip deleted successfully");
      router.replace("/saved");
    } catch (err) {
      console.error("Failed to delete trip:", err);
      toast.error("Failed to delete trip");
    } finally {
      setDeleting(false);
      setShowDeleteDialog(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <main className="flex-1 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="w-10 h-10 text-primary animate-spin" />
            <p className="text-muted-foreground">Loading trip details...</p>
          </div>
        </main>
      </div>
    );
  }

  if (error || !trip) {
    return (
      <div className="min-h-screen flex flex-col bg-background">
        <main className="flex-1 flex items-center justify-center">
          <Card className="p-8 text-center">
            <p className="text-destructive mb-4">{error || "Trip not found"}</p>
            <Link href="/saved">
              <Button>Back to saved trips</Button>
            </Link>
          </Card>
        </main>
      </div>
    );
  }

  const itinerary = trip.itinerary_data;
  const tripOverview = itinerary.trip_overview || itinerary.days || [];

  // Extract hotels from itinerary
  const hotels = tripOverview
    .flatMap(
      (day: any) =>
        day.events?.filter((e: any) => e.event_type === "hotel_checkin") || [],
    )
    .map((event: any) => ({
      name: event.location?.name || "Unknown Hotel",
      price:
        parseInt(event.budget?.split(" ")[0]?.replace("$", "") || "0") || 0,
      wifi: "Good",
      noise: "Quiet",
      why: event.description || "",
    }));

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <main className="flex-1">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">
          {/* Header */}
          <div className="mb-12">
            <div className="flex items-center gap-4 mb-6">
              <Link href="/saved">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to trips
                </Button>
              </Link>
            </div>

            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 mb-8">
              <div>
                <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-3">
                  {trip.name}
                </h1>
              </div>

              <div className="flex gap-3 shrink-0">
                <AlertDialog
                  open={showDeleteDialog}
                  onOpenChange={setShowDeleteDialog}
                >
                  <AlertDialogTrigger asChild>
                    <Button variant="destructive" size="lg">
                      <Trash2 className="w-5 h-5 mr-2" />
                      Delete Trip
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Delete Trip</AlertDialogTitle>
                      <AlertDialogDescription>
                        Are you sure you want to delete &quot;{trip.name}&quot;?
                        This action cannot be undone.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction
                        onClick={handleDelete}
                        disabled={deleting}
                        className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                      >
                        {deleting ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin mr-2" />
                            Deleting...
                          </>
                        ) : (
                          "Delete"
                        )}
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            </div>

            {/* Trip Stats */}
            <div className="grid grid-cols-2 gap-4 md:gap-6">
              <div className="p-4 md:p-6 rounded-xl bg-primary/5 border border-primary/20">
                <p className="text-xs md:text-sm text-muted-foreground mb-2">
                  Total Days
                </p>
                <p className="text-2xl md:text-3xl font-bold text-foreground">
                  {itinerary.total_days || tripOverview.length} Days
                </p>
              </div>
              <div className="p-4 md:p-6 rounded-xl bg-secondary/5 border border-secondary/20">
                <p className="text-xs md:text-sm text-muted-foreground mb-2">
                  Average Daily Budget
                </p>
                <p className="text-2xl md:text-3xl font-bold text-foreground">
                  {itinerary.average_budget_spend_per_day || "N/A"}
                </p>
              </div>
            </div>

            {/* Trip Notes */}
            {trip.notes && (
              <Card className="p-6 rounded-xl bg-muted/30 border-border/50 mt-8">
                <h3 className="text-lg font-semibold text-foreground mb-3">
                  Trip Notes
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  {trip.notes}
                </p>
              </Card>
            )}
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
              {hotels.length > 0 ? (
                hotels.map((hotel: any, i: any) => (
                  <Card
                    key={i}
                    className="p-6 md:p-8 rounded-2xl border-border/50 hover:border-primary/30 transition-colors"
                  >
                    <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                      <div className="flex-1">
                        <h3 className="text-xl md:text-2xl font-bold text-foreground mb-3">
                          {hotel.name}
                        </h3>
                        <p className="text-muted-foreground mb-4">
                          {hotel.why}
                        </p>
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
                ))
              ) : (
                <Card className="p-12 text-center">
                  <p className="text-muted-foreground">
                    No hotel information available
                  </p>
                </Card>
              )}
            </TabsContent>

            {/* Itinerary Tab */}
            <TabsContent value="itinerary" className="space-y-6">
              {tripOverview.length > 0 ? (
                tripOverview.map((day: any, i: any) => (
                  <Card
                    key={i}
                    className="p-6 md:p-8 rounded-2xl border-border/50"
                  >
                    <div className="mb-6">
                      <h3 className="text-xl md:text-2xl font-bold text-foreground mb-2">
                        Day {day.trip_number || i + 1}:{" "}
                        {day.start_date
                          ? new Date(day.start_date).toLocaleDateString(
                              "en-US",
                              {
                                weekday: "long",
                                month: "long",
                                day: "numeric",
                              },
                            )
                          : `Day ${i + 1}`}
                      </h3>
                      <p className="text-muted-foreground">
                        {day.summary || ""}
                      </p>
                    </div>
                    <div className="space-y-4">
                      {day.events?.map((event: any, j: any) => (
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
                                {event.start_time || ""} -{" "}
                                {event.end_time || ""}
                              </span>
                            </div>
                            <h4 className="font-semibold text-foreground mb-1">
                              {event.description || ""}
                            </h4>
                            <div className="flex items-center gap-4 text-sm text-muted-foreground">
                              <div className="flex items-center gap-1">
                                <MapPin className="w-4 h-4" />
                                <span>{event.location?.name || ""}</span>
                              </div>
                              <div className="flex items-center gap-1">
                                <DollarSign className="w-4 h-4" />
                                <span>{event.budget || ""}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      )) || (
                        <p className="text-muted-foreground">
                          No events for this day
                        </p>
                      )}
                    </div>
                  </Card>
                ))
              ) : (
                <Card className="p-12 text-center">
                  <p className="text-muted-foreground">
                    No itinerary information available
                  </p>
                </Card>
              )}
            </TabsContent>
          </Tabs>

          {/* Bottom CTA */}
          <div className="flex flex-col md:flex-row gap-4 items-center justify-center">
            <Link href="/saved">
              <Button
                variant="outline"
                size="lg"
                className="w-full md:w-auto bg-transparent"
              >
                Back to saved trips
              </Button>
            </Link>
            <Link href="/onboarding">
              <Button size="lg" className="w-full md:w-auto">
                Plan another trip
              </Button>
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
