/* eslint-disable @typescript-eslint/no-explicit-any */

import { post } from "@/lib/api-client";

// export interface Recommendation {
//   placeId: string;
//   placeName: string;
//   region: string;
//   description: string;
//   score: number;
//   vibe_compatibility: {
//     lowkey: number;
//     nature: number;
//     crowds: number;
//     social: number;
//   };
// }

// export interface RecommendationResponse {
//   userId: string;
//   recommendations: Recommendation[];
//   totalMatches: number;
// }

export const recommendService = {
  getRecommendations: async (userId: string): Promise<any> => {
    return post<any>(`/recommendations/${userId}/generate`);
  },
};
