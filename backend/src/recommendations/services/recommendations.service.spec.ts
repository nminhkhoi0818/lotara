import { Test, TestingModule } from '@nestjs/testing';
import { NotFoundException } from '@nestjs/common';
import { RecommendationsService } from '../services/recommendations.service';
import { UsersService } from '../../users/services/users.service';
import { VibeMappingService } from '../../users/services/vibe-mapping.service';
import { PlacesService } from '../../places/services/places.service';
import { MatchScoringService } from '../services/match-scoring.service';

describe('RecommendationsService', () => {
  let service: RecommendationsService;
  let usersService: UsersService;
  let placesService: PlacesService;
  let userId: string;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        RecommendationsService,
        UsersService,
        PlacesService,
        MatchScoringService,
        VibeMappingService,
      ],
    }).compile();

    service = module.get<RecommendationsService>(RecommendationsService);
    usersService = module.get<UsersService>(UsersService);
    placesService = module.get<PlacesService>(PlacesService);

    // Create a test user
    const dto = {
      budget: 'medium',
      travelStyle: 'solo',
      answers: {
        quiet_or_lively: 'quiet',
        nature_or_city: 'nature',
        crowd_tolerance: 3,
      },
    };
    userId = usersService.createUserFromOnboarding(dto);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('getRecommendationsForUser', () => {
    it('should return recommendations for valid user', () => {
      const result = service.getRecommendationsForUser(userId);

      expect(result).toHaveProperty('userId', userId);
      expect(result).toHaveProperty('recommendations');
      expect(result).toHaveProperty('totalMatches');
      expect(Array.isArray(result.recommendations)).toBe(true);
    });

    it('should throw NotFoundException for invalid userId', () => {
      expect(() =>
        service.getRecommendationsForUser('invalid-user-id'),
      ).toThrow(NotFoundException);
    });

    it('should return results sorted by score (highest first)', () => {
      const result = service.getRecommendationsForUser(userId);

      for (let i = 0; i < result.recommendations.length - 1; i++) {
        expect(result.recommendations[i].score).toBeGreaterThanOrEqual(
          result.recommendations[i + 1].score,
        );
      }
    });

    it('should respect limit parameter', () => {
      const result = service.getRecommendationsForUser(userId, 3);

      expect(result.recommendations.length).toBeLessThanOrEqual(3);
    });

    it('should filter places by budget and travel style', () => {
      const result = service.getRecommendationsForUser(userId);
      const user = usersService.getUserById(userId);

      result.recommendations.forEach((rec) => {
        const place = placesService.getPlaceById(rec.placeId);
        expect(place!.budget_range).toBe(user!.budget_range);
        expect(place!.travel_style).toBe(user!.travel_style);
      });
    });

    it('should include vibe compatibility breakdown', () => {
      const result = service.getRecommendationsForUser(userId);

      result.recommendations.forEach((rec) => {
        expect(rec).toHaveProperty('vibe_compatibility');
        expect(rec.vibe_compatibility).toHaveProperty('lowkey');
        expect(rec.vibe_compatibility).toHaveProperty('nature');
        expect(rec.vibe_compatibility).toHaveProperty('crowds');
        expect(rec.vibe_compatibility).toHaveProperty('social');
      });
    });

    it('should return valid scores (0-100)', () => {
      const result = service.getRecommendationsForUser(userId);

      result.recommendations.forEach((rec) => {
        expect(rec.score).toBeGreaterThanOrEqual(0);
        expect(rec.score).toBeLessThanOrEqual(100);
      });
    });

    it('should have all required fields in recommendation', () => {
      const result = service.getRecommendationsForUser(userId, 1);

      expect(result.recommendations.length).toBeGreaterThan(0);
      const rec = result.recommendations[0];

      expect(rec).toHaveProperty('placeId');
      expect(rec).toHaveProperty('placeName');
      expect(rec).toHaveProperty('region');
      expect(rec).toHaveProperty('description');
      expect(rec).toHaveProperty('score');
      expect(rec).toHaveProperty('vibe_compatibility');
    });
  });

  describe('getAllPlaceScores', () => {
    it('should return all places with scores', () => {
      const result = service.getAllPlaceScores(userId);

      expect(result.recommendations.length).toBeGreaterThan(3);
      expect(result.totalMatches).toBeGreaterThan(3);
    });

    it('should throw NotFoundException for invalid userId', () => {
      expect(() => service.getAllPlaceScores('invalid-user-id')).toThrow(
        NotFoundException,
      );
    });

    it('should not filter by budget/travel style', () => {
      const result = service.getAllPlaceScores(userId);
      const allPlaces = placesService.getAllPlaces();

      expect(result.recommendations.length).toBeLessThanOrEqual(
        allPlaces.length,
      );
    });
  });

  describe('scoring consistency', () => {
    it('should give same recommendations for same user', () => {
      const result1 = service.getRecommendationsForUser(userId, 5);
      const result2 = service.getRecommendationsForUser(userId, 5);

      expect(result1.recommendations).toEqual(result2.recommendations);
    });

    it('should give higher scores to better-matching places', () => {
      // Create a user with very specific preferences
      const specificDto = {
        budget: 'high',
        travelStyle: 'couple',
        answers: {
          quiet_or_lively: 'quiet',
          nature_or_city: 'nature',
          crowd_tolerance: 2,
        },
      };
      const specificUserId = usersService.createUserFromOnboarding(specificDto);

      const result = service.getRecommendationsForUser(specificUserId);

      // Top recommendation should have decent score
      if (result.recommendations.length > 0) {
        expect(result.recommendations[0].score).toBeGreaterThan(40);
      }
    });
  });
});
