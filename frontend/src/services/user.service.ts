import { post, get, del } from "@/lib/api-client";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

export interface OnboardingData {
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

export interface OnboardingResponse {
  userId: string;
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

export interface SaveTripResponse {
  id: string;
  user_id: string;
  name: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  itinerary_data: any;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface StreamEvent {
  type: "user" | "ai_chunk" | "complete" | "error";
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data?: any;
}

export const userService = {
  submitOnboarding: async (
    data: OnboardingData,
  ): Promise<OnboardingResponse> => {
    return post<OnboardingResponse, OnboardingData>(
      "/users/onboarding/submit",
      data,
    );
  },

  getPersonaSummary: async (
    data: OnboardingData,
    onEvent?: (event: StreamEvent) => void,
  ): Promise<string> => {
    return new Promise(async (resolve, reject) => {
      try {
        const response = await fetch(
          `${API_BASE_URL}/users/onboarding/submit?stream=true`,
          {
            method: "POST",
            body: JSON.stringify(data),
            headers: {
              "Content-Type": "application/json",
            },
          },
        );

        if (!response.body) {
          throw new Error("No response body");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let fullSummary = "";

        const processChunk = (chunk: string) => {
          buffer += chunk;
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const parsed: StreamEvent = JSON.parse(line.slice(6));
                if (onEvent) {
                  onEvent(parsed);
                }

                if (parsed.type === "ai_chunk") {
                  fullSummary += parsed.data;
                } else if (parsed.type === "complete") {
                  resolve(fullSummary);
                  return;
                } else if (parsed.type === "error") {
                  reject(new Error(parsed.data || "Stream error"));
                  return;
                }
              } catch (error) {
                console.error("Failed to parse SSE event:", error);
              }
            }
          }
        };

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          processChunk(decoder.decode(value, { stream: true }));
        }
        processChunk(decoder.decode());
      } catch (error) {
        reject(error);
      }
    });
  },

  getUserById: async (userId: string): Promise<OnboardingResponse> => {
    return get<OnboardingResponse>(`/users/${userId}`);
  },

  saveTrip: async (
    userId: string,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    tripData: any,
  ): Promise<SaveTripResponse> => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return post<SaveTripResponse, any>(
      `/users/${userId}/saved-trips`,
      tripData,
    );
  },

  getAllSavedTrips: async (userId: string): Promise<SaveTripResponse[]> => {
    return get<SaveTripResponse[]>(`/users/${userId}/saved-trips`);
  },

  getSavedTripById: async (
    userId: string,
    tripId: string,
  ): Promise<SaveTripResponse> => {
    return get<SaveTripResponse>(`/users/${userId}/saved-trips/${tripId}`);
  },

  deleteSavedTrip: async (userId: string, tripId: string): Promise<void> => {
    return del<void>(`/users/${userId}/saved-trips/${tripId}`);
  },
};
