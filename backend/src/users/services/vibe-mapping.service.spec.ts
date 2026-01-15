import { Test, TestingModule } from '@nestjs/testing';
import { VibeMappingService } from '../services/vibe-mapping.service';
import { BadRequestException } from '@nestjs/common';

describe('VibeMappingService', () => {
  let service: VibeMappingService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [VibeMappingService],
    }).compile();

    service = module.get<VibeMappingService>(VibeMappingService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('mapAnswersToVibe', () => {
    it('should map quiet answer correctly', () => {
      const answers = {
        quiet_or_lively: 'quiet',
      };

      const result = service.mapAnswersToVibe(answers);

      expect(result.lowkey).toBe(8);
      expect(result.social).toBe(3);
    });

    it('should map lively answer correctly', () => {
      const answers = {
        quiet_or_lively: 'lively',
      };

      const result = service.mapAnswersToVibe(answers);

      expect(result.lowkey).toBe(2);
      expect(result.social).toBe(8);
    });

    it('should map nature answer correctly', () => {
      const answers = {
        nature_or_city: 'nature',
      };

      const result = service.mapAnswersToVibe(answers);

      expect(result.nature).toBe(9);
    });

    it('should map city answer correctly', () => {
      const answers = {
        nature_or_city: 'city',
      };

      const result = service.mapAnswersToVibe(answers);

      expect(result.nature).toBe(3);
    });

    it('should map crowd_tolerance correctly', () => {
      const answers = {
        crowd_tolerance: 7,
      };

      const result = service.mapAnswersToVibe(answers);

      expect(result.crowds).toBe(7);
    });

    it('should map all answers together correctly', () => {
      const answers = {
        quiet_or_lively: 'quiet',
        nature_or_city: 'nature',
        crowd_tolerance: 2,
      };

      const result = service.mapAnswersToVibe(answers);

      expect(result.lowkey).toBe(8);
      expect(result.social).toBe(3);
      expect(result.nature).toBe(9);
      expect(result.crowds).toBe(2);
    });

    it('should use default values for missing answers', () => {
      const answers = {};

      const result = service.mapAnswersToVibe(answers);

      expect(result.lowkey).toBe(5);
      expect(result.nature).toBe(5);
      expect(result.crowds).toBe(5);
      expect(result.social).toBe(5);
    });

    it('should throw error for crowd_tolerance < 0', () => {
      const answers = {
        crowd_tolerance: -1,
      };

      expect(() => service.mapAnswersToVibe(answers)).toThrow(
        BadRequestException,
      );
    });

    it('should throw error for crowd_tolerance > 10', () => {
      const answers = {
        crowd_tolerance: 11,
      };

      expect(() => service.mapAnswersToVibe(answers)).toThrow(
        BadRequestException,
      );
    });

    it('should accept crowd_tolerance boundary values', () => {
      const answers0 = { crowd_tolerance: 0 };
      const answers10 = { crowd_tolerance: 10 };

      expect(() => service.mapAnswersToVibe(answers0)).not.toThrow();
      expect(() => service.mapAnswersToVibe(answers10)).not.toThrow();

      expect(service.mapAnswersToVibe(answers0).crowds).toBe(0);
      expect(service.mapAnswersToVibe(answers10).crowds).toBe(10);
    });

    it('should always include all vibe keys', () => {
      const answers = {};

      const result = service.mapAnswersToVibe(answers);

      expect(result).toHaveProperty('lowkey');
      expect(result).toHaveProperty('nature');
      expect(result).toHaveProperty('crowds');
      expect(result).toHaveProperty('social');
    });

    it('should ensure all vibe values are in range [0, 10]', () => {
      const testCases = [
        { quiet_or_lively: 'quiet' },
        { quiet_or_lively: 'lively' },
        { nature_or_city: 'nature' },
        { nature_or_city: 'city' },
        { crowd_tolerance: 5 },
      ];

      testCases.forEach((answers) => {
        const result = service.mapAnswersToVibe(answers);
        expect(result.lowkey).toBeGreaterThanOrEqual(0);
        expect(result.lowkey).toBeLessThanOrEqual(10);
        expect(result.nature).toBeGreaterThanOrEqual(0);
        expect(result.nature).toBeLessThanOrEqual(10);
        expect(result.crowds).toBeGreaterThanOrEqual(0);
        expect(result.crowds).toBeLessThanOrEqual(10);
        expect(result.social).toBeGreaterThanOrEqual(0);
        expect(result.social).toBeLessThanOrEqual(10);
      });
    });

    it('should be deterministic - same input produces same output', () => {
      const answers = {
        quiet_or_lively: 'quiet',
        nature_or_city: 'nature',
        crowd_tolerance: 5,
      };

      const result1 = service.mapAnswersToVibe(answers);
      const result2 = service.mapAnswersToVibe(answers);

      expect(result1).toEqual(result2);
    });
  });
});
