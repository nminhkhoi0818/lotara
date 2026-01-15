import { Test, TestingModule } from '@nestjs/testing';
import { MatchScoringService } from '../services/match-scoring.service';

describe('MatchScoringService', () => {
  let service: MatchScoringService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [MatchScoringService],
    }).compile();

    service = module.get<MatchScoringService>(MatchScoringService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('calculateMatchScore', () => {
    it('should return perfect score (100) for identical vibes', () => {
      const userVibe = { lowkey: 8, nature: 9, crowds: 2, social: 3 };
      const placeVibe = { lowkey: 8, nature: 9, crowds: 2, social: 3 };

      const result = service.calculateMatchScore(userVibe, placeVibe);

      expect(result.score).toBe(100);
      expect(result.reasoning.lowkey).toBe(0);
      expect(result.reasoning.nature).toBe(0);
      expect(result.reasoning.crowds).toBe(0);
      expect(result.reasoning.social).toBe(0);
    });

    it('should return lower score for different vibes', () => {
      const userVibe = { lowkey: 8, nature: 9, crowds: 2, social: 3 };
      const placeVibe = { lowkey: 2, nature: 3, crowds: 9, social: 9 };

      const result = service.calculateMatchScore(userVibe, placeVibe);

      expect(result.score).toBeLessThan(100);
      expect(result.score).toBeGreaterThan(0);
    });

    it('should calculate correct score for partial match', () => {
      const userVibe = { lowkey: 8, nature: 9, crowds: 2, social: 3 };
      // Average diff: (0 + 0 + 2 + 2) / 4 = 1
      // Score: 100 - 1 * 10 = 90
      const placeVibe = { lowkey: 8, nature: 9, crowds: 4, social: 5 };

      const result = service.calculateMatchScore(userVibe, placeVibe);

      expect(result.score).toBe(90);
    });

    it('should clamp score to 0-100 range', () => {
      const userVibe = { lowkey: 0, nature: 0, crowds: 0, social: 0 };
      const placeVibe = { lowkey: 10, nature: 10, crowds: 10, social: 10 };

      const result = service.calculateMatchScore(userVibe, placeVibe);

      expect(result.score).toBeGreaterThanOrEqual(0);
      expect(result.score).toBeLessThanOrEqual(100);
    });

    it('should be symmetric (order independent)', () => {
      const userVibe = { lowkey: 5, nature: 6, crowds: 3, social: 4 };
      const placeVibe = { lowkey: 7, nature: 8, crowds: 5, social: 6 };

      const result1 = service.calculateMatchScore(userVibe, placeVibe);
      const result2 = service.calculateMatchScore(placeVibe, userVibe);

      expect(result1.score).toBe(result2.score);
    });

    it('should calculate individual key differences correctly', () => {
      const userVibe = { lowkey: 5, nature: 5, crowds: 5, social: 5 };
      const placeVibe = { lowkey: 6, nature: 7, crowds: 3, social: 8 };

      const result = service.calculateMatchScore(userVibe, placeVibe);

      expect(result.reasoning.lowkey).toBe(1);
      expect(result.reasoning.nature).toBe(2);
      expect(result.reasoning.crowds).toBe(2);
      expect(result.reasoning.social).toBe(3);
    });
  });

  describe('calculateKeyCompatibility', () => {
    it('should return 100 for identical values', () => {
      const compatibility = service.calculateKeyCompatibility(5, 5);
      expect(compatibility).toBe(100);
    });

    it('should return 90 for difference of 1', () => {
      const compatibility = service.calculateKeyCompatibility(5, 6);
      expect(compatibility).toBe(90);
    });

    it('should return 50 for difference of 5', () => {
      const compatibility = service.calculateKeyCompatibility(5, 10);
      expect(compatibility).toBe(50);
    });

    it('should return 0 for maximum difference (10)', () => {
      const compatibility = service.calculateKeyCompatibility(0, 10);
      expect(compatibility).toBe(0);
    });
  });

  describe('determinism', () => {
    it('should return same score for same input', () => {
      const userVibe = { lowkey: 7, nature: 8, crowds: 3, social: 5 };
      const placeVibe = { lowkey: 6, nature: 7, crowds: 4, social: 6 };

      const result1 = service.calculateMatchScore(userVibe, placeVibe);
      const result2 = service.calculateMatchScore(userVibe, placeVibe);

      expect(result1.score).toBe(result2.score);
      expect(result1.reasoning).toEqual(result2.reasoning);
    });
  });
});
