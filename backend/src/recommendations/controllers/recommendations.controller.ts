import { Controller, Get, Param, Query } from '@nestjs/common';
import { RecommendationsService } from '../services/recommendations.service';

@Controller('recommendations')
export class RecommendationsController {
  constructor(private recommendationsService: RecommendationsService) {}

  /**
   * GET /recommendations/:userId
   *
   * Get personalized place recommendations for a user.
   *
   * Query Parameters:
   * - limit: Maximum number of recommendations (default: 10)
   *
   * Response:
   * {
   *   "userId": "uuid",
   *   "recommendations": [
   *     {
   *       "placeId": "place-1",
   *       "placeName": "Halong Bay",
   *       "region": "Quang Ninh",
   *       "description": "...",
   *       "score": 92,
   *       "vibe_compatibility": {
   *         "lowkey": 3,
   *         "nature": 0,
   *         "crowds": 2,
   *         "social": 2
   *       }
   *     },
   *     ...
   *   ],
   *   "totalMatches": 4
   * }
   *
   * @param userId User ID
   * @param limit Maximum number of results
   * @returns Ranked recommendations
   */
  @Get(':userId')
  async getRecommendations(
    @Param('userId') userId: string,
    @Query('limit') limit?: string,
  ) {
    const limitNum = limit ? Math.min(parseInt(limit), 50) : 10;
    return this.recommendationsService.getRecommendationsForUser(
      userId,
      limitNum,
    );
  }

  /**
   * GET /recommendations/:userId/all
   *
   * Get scores for all places (for debugging/analytics).
   *
   * @param userId User ID
   * @returns All places scored and ranked
   */
  @Get(':userId/all')
  async getAllPlaceScores(@Param('userId') userId: string) {
    return this.recommendationsService.getAllPlaceScores(userId);
  }
}
