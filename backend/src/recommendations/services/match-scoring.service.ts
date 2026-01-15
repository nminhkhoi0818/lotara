import { Injectable } from '@nestjs/common';
import { VibeVector } from '../../users/entities/user.entity';

export interface MatchScore {
  placeId: string;
  placeName: string;
  score: number;
  reasoning: {
    lowkey_match: number;
    nature_match: number;
    crowds_match: number;
    social_match: number;
  };
}

/**
 * Service responsible for calculating match scores between user and place vibes.
 * Uses deterministic scoring algorithm as specified in project design.
 */
@Injectable()
export class MatchScoringService {
  /**
   * Calculate match score between user vibe and place vibe.
   *
   * Formula: score = 100 - avg(|userVibe - placeVibe|) * 10
   *
   * How it works:
   * - For each vibe key, calculate absolute difference
   * - Average all differences
   * - Convert to 0-100 score (lower difference = higher score)
   *
   * @param userVibe User's vibe vector
   * @param placeVibe Place's vibe vector
   * @returns Score object with breakdown
   */
  calculateMatchScore(
    userVibe: VibeVector,
    placeVibe: VibeVector,
  ): {
    score: number;
    reasoning: Record<keyof VibeVector, number>;
  } {
    const vibeKeys: (keyof VibeVector)[] = [
      'lowkey',
      'nature',
      'crowds',
      'social',
    ];
    const differences: number[] = [];
    const reasoning: Record<keyof VibeVector, number> = {} as Record<
      keyof VibeVector,
      number
    >;

    // Calculate absolute difference for each vibe key
    vibeKeys.forEach((key) => {
      const difference = Math.abs(userVibe[key] - placeVibe[key]);
      differences.push(difference);
      reasoning[key] = difference;
    });

    // Average the differences
    const averageDifference =
      differences.reduce((a, b) => a + b, 0) / differences.length;

    // Convert to 0-100 score: lower difference = higher score
    const score = Math.round(100 - averageDifference * 10);

    return {
      score: Math.max(0, Math.min(100, score)), // Clamp to 0-100
      reasoning,
    };
  }

  /**
   * Calculate 0-100 compatibility for a specific vibe key.
   * Useful for detailed explanations.
   *
   * @param userValue User's vibe value for key
   * @param placeValue Place's vibe value for key
   * @returns 0-100 compatibility score
   */
  calculateKeyCompatibility(userValue: number, placeValue: number): number {
    const difference = Math.abs(userValue - placeValue);
    return Math.round(100 - difference * 10);
  }

  /**
   * Generate human-readable reasoning for match.
   *
   * @param vibeKey The vibe key
   * @param userValue User's value
   * @param placeValue Place's value
   * @returns Explanation string
   */
  generateVibeExplanation(
    vibeKey: string,
    userValue: number,
    placeValue: number,
  ): string {
    const compatibility = this.calculateKeyCompatibility(userValue, placeValue);

    const explanations: Record<string, () => string> = {
      lowkey: () => {
        if (compatibility > 80) {
          return userValue > 5
            ? 'Peaceful and relaxing atmosphere'
            : 'Energetic and lively environment';
        }
        return userValue > placeValue
          ? 'Busier than you prefer'
          : 'More quiet than you might like';
      },
      nature: () => {
        if (compatibility > 80) {
          return userValue > 5
            ? 'Abundant natural scenery'
            : 'Primarily urban setting';
        }
        return userValue > placeValue
          ? 'Less nature-focused than desired'
          : 'More natural than expected';
      },
      crowds: () => {
        if (compatibility > 80) {
          return userValue > 5
            ? 'Popular tourist destination'
            : 'Off-the-beaten-path location';
        }
        return userValue > placeValue
          ? 'More crowded than preferred'
          : 'Less touristy than expected';
      },
      social: () => {
        if (compatibility > 80) {
          return userValue > 5
            ? 'Great for meeting people'
            : 'Good for solo travelers';
        }
        return userValue > placeValue
          ? 'More social activities available'
          : 'Quieter social scene';
      },
    };

    return explanations[vibeKey]?.() || `Vibe compatibility: ${compatibility}%`;
  }
}
