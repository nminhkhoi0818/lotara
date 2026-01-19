import { Injectable, NotFoundException } from '@nestjs/common';
import { UsersService } from '../../users/services/users.service';
import { PlacesService } from '../../places/services/places.service';
import { MatchScoringService, MatchScore } from './match-scoring.service';

export interface RecommendationResult {
  userId: string;
  recommendations: Array<{
    placeId: string;
    placeName: string;
    region: string;
    description: string;
    score: number;
    vibe_compatibility: {
      lowkey: number;
      nature: number;
      crowds: number;
      social: number;
    };
  }>;
  totalMatches: number;
}

/**
 * Service that orchestrates user-place recommendation matching.
 *
 * Steps:
 * 1. Retrieve user by ID
 * 2. Load all places matching user's budget and travel style
 * 3. Score each place against user's vibe
 * 4. Rank and return results
 */
@Injectable()
export class RecommendationsService {
  constructor(
    private usersService: UsersService,
    private placesService: PlacesService,
    private matchScoringService: MatchScoringService,
  ) {}

  /**
   * Get personalized place recommendations for a user.
   *
   * @param userId User ID
   * @param limit Maximum number of recommendations (default: 10)
   * @returns Ranked recommendations
   * @throws NotFoundException if user not found
   */
  async getRecommendationsForUser(
    userId: string,
    limit: number = 10,
  ): Promise<RecommendationResult> {
    // Step 1: Retrieve user
    const user = await this.usersService.getUserById(userId);
    if (!user) {
      throw new NotFoundException(`User ${userId} not found`);
    }

    // Step 2: Filter places by budget and travel style
    const candidatePlaces = this.placesService.filterPlacesByPreferences(
      user.budget_range,
      user.travel_style,
    );

    // Step 3: Score each place
    const scoredPlaces = candidatePlaces.map((place) => {
      const { score, reasoning } = this.matchScoringService.calculateMatchScore(
        user.vibe_vector,
        place.vibe_vector,
      );

      return {
        placeId: place.id,
        placeName: place.name,
        region: place.region,
        description: place.description,
        score,
        vibe_compatibility: reasoning,
      };
    });

    // Step 4: Sort by score (descending) and limit results
    const recommendations = scoredPlaces
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);

    return {
      userId,
      recommendations,
      totalMatches: recommendations.length,
    };
  }

  /**
   * Get detailed scoring breakdown for all places (for debugging/understanding).
   *
   * @param userId User ID
   * @returns All places with scores
   */
  async getAllPlaceScores(userId: string): Promise<RecommendationResult> {
    const user = await this.usersService.getUserById(userId);
    if (!user) {
      throw new NotFoundException(`User ${userId} not found`);
    }

    const allPlaces = this.placesService.getAllPlaces();

    const scoredPlaces = allPlaces.map((place) => {
      const { score, reasoning } = this.matchScoringService.calculateMatchScore(
        user.vibe_vector,
        place.vibe_vector,
      );

      return {
        placeId: place.id,
        placeName: place.name,
        region: place.region,
        description: place.description,
        score,
        vibe_compatibility: reasoning,
      };
    });

    return {
      userId,
      recommendations: scoredPlaces.sort((a, b) => b.score - a.score),
      totalMatches: scoredPlaces.length,
    };
  }

  /**
   * Get recommendations filtered by budget and travel style.
   *
   * @param userId User ID
   * @param limit Maximum number of recommendations
   * @returns Filtered recommendations
   */
  async getFilteredRecommendations(
    userId: string,
    limit?: number,
  ): Promise<RecommendationResult> {
    return await this.getRecommendationsForUser(userId, limit);
  }
}
