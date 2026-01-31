import { post, get } from "@/lib/api-client";

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

export const userService = {
  submitOnboarding: async (
    data: OnboardingData,
  ): Promise<OnboardingResponse> => {
    return post<OnboardingResponse, OnboardingData>(
      "/users/onboarding/submit",
      data,
    );
  },

  getUserById: async (userId: string): Promise<OnboardingResponse> => {
    return get<OnboardingResponse>(`/users/${userId}`);
  },
};
