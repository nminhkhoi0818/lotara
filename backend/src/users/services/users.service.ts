import { Injectable } from '@nestjs/common';
import { User, BudgetRange, TravelStyle } from '../entities/user.entity';
import { CreateUserOnboardingDto } from '../dto/create-user-onboarding.dto';
import { VibeMappingService } from './vibe-mapping.service';

/**
 * Service for managing user data and persistence.
 *
 * This is a simple in-memory implementation for MVP.
 * In production, this would integrate with TypeORM/database.
 */
@Injectable()
export class UsersService {
  private users: Map<string, User> = new Map();

  constructor(private vibeMappingService: VibeMappingService) {}

  /**
   * Creates a new user from onboarding data.
   *
   * Steps:
   * 1. Map answers to vibe vector
   * 2. Create User entity
   * 3. Persist user
   * 4. Return userId
   *
   * @param createUserOnboardingDto Onboarding request
   * @returns User ID
   */
  createUserFromOnboarding(
    createUserOnboardingDto: CreateUserOnboardingDto,
  ): string {
    // Map answers to vibe vector
    const vibeVector = this.vibeMappingService.mapAnswersToVibe(
      createUserOnboardingDto.answers,
    );

    // Create user entity
    const user = new User(
      vibeVector,
      createUserOnboardingDto.budget as BudgetRange,
      createUserOnboardingDto.travelStyle as TravelStyle,
    );

    // Persist user (in-memory storage)
    this.users.set(user.id, user);

    return user.id;
  }

  /**
   * Retrieves a user by ID (for testing/debugging).
   *
   * @param userId User ID
   * @returns User or undefined
   */
  getUserById(userId: string): User | undefined {
    return this.users.get(userId);
  }

  /**
   * Gets all users (for testing/debugging).
   *
   * @returns Array of all users
   */
  getAllUsers(): User[] {
    return Array.from(this.users.values());
  }
}
