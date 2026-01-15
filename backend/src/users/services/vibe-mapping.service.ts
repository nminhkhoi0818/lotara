import { Injectable, BadRequestException } from '@nestjs/common';
import { VibeVector, BudgetRange, TravelStyle } from '../entities/user.entity';
import { OnboardingAnswersDto } from '../dto/create-user-onboarding.dto';

/**
 * Service responsible for mapping user answers to vibe vector values.
 * This service implements pure, deterministic vibe mapping logic.
 */
@Injectable()
export class VibeMappingService {
  /**
   * Converts onboarding answers into a normalized vibe vector.
   *
   * Mapping rules:
   * - quiet → lowkey=8, social=3
   * - lively → lowkey=2, social=8
   * - nature → nature=9
   * - city → nature=3
   * - crowd_tolerance → crowds=provided value
   *
   * @param answers User's onboarding answers
   * @returns Normalized vibe vector with all keys present and values 0-10
   * @throws BadRequestException if validation fails
   */
  mapAnswersToVibe(answers: OnboardingAnswersDto): VibeVector {
    const vibe: VibeVector = {
      lowkey: 5, // Default neutral value
      nature: 5,
      crowds: 5,
      social: 5,
    };

    // Process quiet_or_lively
    if (answers.quiet_or_lively !== undefined) {
      if (answers.quiet_or_lively === 'quiet') {
        vibe.lowkey = 8;
        vibe.social = 3;
      } else if (answers.quiet_or_lively === 'lively') {
        vibe.lowkey = 2;
        vibe.social = 8;
      }
    }

    // Process nature_or_city
    if (answers.nature_or_city !== undefined) {
      if (answers.nature_or_city === 'nature') {
        vibe.nature = 9;
      } else if (answers.nature_or_city === 'city') {
        vibe.nature = 3;
      }
    }

    // Process crowd_tolerance
    if (answers.crowd_tolerance !== undefined) {
      if (answers.crowd_tolerance < 0 || answers.crowd_tolerance > 10) {
        throw new BadRequestException(
          'crowd_tolerance must be between 0 and 10',
        );
      }
      vibe.crowds = answers.crowd_tolerance;
    }

    // Validate all vibe values are in range [0, 10]
    this.validateVibeVector(vibe);

    return vibe;
  }

  /**
   * Validates that all vibe values are integers in the range [0, 10].
   *
   * @param vibe The vibe vector to validate
   * @throws BadRequestException if validation fails
   */
  private validateVibeVector(vibe: VibeVector): void {
    const requiredKeys: (keyof VibeVector)[] = [
      'lowkey',
      'nature',
      'crowds',
      'social',
    ];

    // Check all required keys exist
    for (const key of requiredKeys) {
      if (vibe[key] === undefined) {
        throw new BadRequestException(`Missing required vibe key: ${key}`);
      }

      // Check value is a number
      if (typeof vibe[key] !== 'number') {
        throw new BadRequestException(`Vibe value for ${key} must be a number`);
      }

      // Check value is in range
      if (vibe[key] < 0 || vibe[key] > 10) {
        throw new BadRequestException(
          `Vibe value for ${key} must be between 0 and 10, got ${vibe[key]}`,
        );
      }

      // Check value is integer
      if (!Number.isInteger(vibe[key])) {
        throw new BadRequestException(
          `Vibe value for ${key} must be an integer, got ${vibe[key]}`,
        );
      }
    }
  }
}
