import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import {
  User,
  BudgetRange,
  TravelStyle,
  PersonaAnswers,
} from '../entities/user.entity';
import { CreateUserOnboardingDto } from '../dto/create-user-onboarding.dto';
import { SubmitUserOnboardingDto } from '../dto/submit-user-onboarding.dto';
import { VibeMappingService } from './vibe-mapping.service';
import { GeminiService } from './gemini.service';

/**
 * Service for managing user data and persistence.
 *
 * Uses TypeORM Repository for database operations.
 */
@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private userRepository: Repository<User>,
    private vibeMappingService: VibeMappingService,
    private geminiService: GeminiService,
  ) {}

  /**
   * Creates a new user from onboarding data.
   *
   * Steps:
   * 1. Map answers to vibe vector
   * 2. Create User entity
   * 3. Persist user to database
   * 4. Return userId
   *
   * @param createUserOnboardingDto Onboarding request
   * @returns User ID
   */
  async createUserFromOnboarding(
    createUserOnboardingDto: CreateUserOnboardingDto,
  ): Promise<string> {
    // Map answers to vibe vector
    const vibeVector = this.vibeMappingService.mapAnswersToVibe(
      createUserOnboardingDto.answers,
    );

    // Create user entity
    const user = this.userRepository.create({
      vibe_vector: vibeVector,
      budget_range: createUserOnboardingDto.budget as BudgetRange,
      travel_style: createUserOnboardingDto.travelStyle as TravelStyle,
    });

    // Persist user to database
    const savedUser = await this.userRepository.save(user);

    return savedUser.id;
  }

  /**
   * Retrieves a user by ID.
   *
   * @param userId User ID
   * @returns User or null
   */
  async getUserById(userId: string): Promise<User | null> {
    return await this.userRepository.findOne({ where: { id: userId } });
  }

  /**
   * Gets all users (for testing/debugging).
   *
   * @returns Array of all users
   */
  async getAllUsers(): Promise<User[]> {
    return await this.userRepository.find();
  }

  /**
   * Submits user onboarding answers and creates a user with persona.
   *
   * This endpoint accepts the full persona questionnaire from the frontend
   * and creates a user with the persona data stored in the database.
   *
   * @param submitUserOnboardingDto Persona answers from frontend
   * @returns Created user with persona data
   */
  async submitUserOnboarding(
    submitUserOnboardingDto: SubmitUserOnboardingDto,
  ): Promise<User> {
    // Convert DTO to PersonaAnswers
    const personaAnswers: PersonaAnswers = {
      duration: submitUserOnboardingDto.duration as any,
      companions: submitUserOnboardingDto.companions as any,
      budget: submitUserOnboardingDto.budget as any,
      pace: submitUserOnboardingDto.pace as any,
      travelStyle: submitUserOnboardingDto.travelStyle as any,
      activity: submitUserOnboardingDto.activity as any,
      crowds: submitUserOnboardingDto.crowds as any,
      accommodation: submitUserOnboardingDto.accommodation as any,
      remote: submitUserOnboardingDto.remote,
      timing: submitUserOnboardingDto.timing as any,
    };

    // For now, create a basic vibe vector based on persona answers
    // This is a simple mapping logic that can be enhanced with AI later
    const vibeVector = {
      lowkey: this.calculateLowkeyScore(personaAnswers),
      nature: this.calculateNatureScore(personaAnswers),
      crowds: this.calculateCrowdsScore(personaAnswers),
      social: this.calculateSocialScore(personaAnswers),
    };

    // Map to legacy budget range and travel style
    const budgetRange = this.mapBudgetToBudgetRange(personaAnswers.budget);
    const travelStyle = this.mapCompanionsToTravelStyle(
      personaAnswers.companions,
    );

    // Create user entity with persona data
    const user = this.userRepository.create({
      vibe_vector: vibeVector,
      budget_range: budgetRange,
      travel_style: travelStyle,
      persona_answers: personaAnswers,
    });

    // Persist user to database
    return await this.userRepository.save(user);
  }

  /**
   * Submits user onboarding answers and generates AI welcome message.
   *
   * @param submitUserOnboardingDto Persona answers from frontend
   * @returns Object containing created user and AI-generated message
   */
  async submitUserOnboardingWithAI(
    submitUserOnboardingDto: SubmitUserOnboardingDto,
  ): Promise<{ user: User; aiMessage: string }> {
    // Create user first
    const user = await this.submitUserOnboarding(submitUserOnboardingDto);

    // Generate AI welcome message
    const aiMessage = await this.geminiService.generateWelcomeMessage(
      user.persona_answers!,
    );

    return { user, aiMessage };
  }

  /**
   * Submits user onboarding and returns streaming AI message.
   *
   * @param submitUserOnboardingDto Persona answers from frontend
   * @returns Object containing user and async generator for AI message stream
   */
  async submitUserOnboardingWithAIStream(
    submitUserOnboardingDto: SubmitUserOnboardingDto,
  ): Promise<{
    user: User;
    aiMessageStream: AsyncGenerator<string, void, unknown>;
  }> {
    // Create user first
    const user = await this.submitUserOnboarding(submitUserOnboardingDto);

    // Get AI message stream
    const aiMessageStream = this.geminiService.generateWelcomeMessageStream(
      user.persona_answers!,
    );

    return { user, aiMessageStream };
  }

  /**
   * Calculate lowkey score based on persona answers
   * Range: 0-10 (0 = not lowkey, 10 = very lowkey)
   */
  private calculateLowkeyScore(persona: PersonaAnswers): number {
    let score = 5; // baseline

    // Pace affects lowkey score
    if (persona.pace === 'slow') score += 3;
    else if (persona.pace === 'balanced') score += 1;
    else if (persona.pace === 'fast') score -= 2;

    // Crowds preference
    if (persona.crowds === 'avoid') score += 2;
    else if (persona.crowds === 'embrace') score -= 2;

    // Activity level
    if (persona.activity === 'low') score += 2;
    else if (persona.activity === 'high') score -= 2;

    // Travel style
    if (persona.travelStyle === 'wellness') score += 2;
    else if (persona.travelStyle === 'adventure') score -= 2;

    return Math.max(0, Math.min(10, score));
  }

  /**
   * Calculate nature score based on persona answers
   * Range: 0-10 (0 = city lover, 10 = nature lover)
   */
  private calculateNatureScore(persona: PersonaAnswers): number {
    let score = 5; // baseline

    // Travel style is the main indicator
    if (persona.travelStyle === 'nature') score += 4;
    else if (persona.travelStyle === 'cultural') score -= 2;
    else if (persona.travelStyle === 'adventure') score += 2;

    // Crowds preference
    if (persona.crowds === 'avoid') score += 1;

    return Math.max(0, Math.min(10, score));
  }

  /**
   * Calculate crowds tolerance score
   * Range: 0-10 (0 = avoid crowds, 10 = embrace crowds)
   */
  private calculateCrowdsScore(persona: PersonaAnswers): number {
    if (persona.crowds === 'avoid') return 2;
    if (persona.crowds === 'mixed') return 5;
    if (persona.crowds === 'embrace') return 8;
    return 5;
  }

  /**
   * Calculate social score based on persona answers
   * Range: 0-10 (0 = not social, 10 = very social)
   */
  private calculateSocialScore(persona: PersonaAnswers): number {
    let score = 5; // baseline

    // Companions affect social score
    if (persona.companions === 'solo') score -= 1;
    else if (persona.companions === 'friends') score += 3;
    else if (persona.companions === 'couple') score += 0;
    else score += 2; // family

    // Accommodation type
    if (persona.accommodation === 'hostel') score += 3;
    else if (persona.accommodation === 'premium') score -= 1;

    // Travel style
    if (persona.travelStyle === 'cultural') score += 2;
    else if (persona.travelStyle === 'food') score += 2;

    return Math.max(0, Math.min(10, score));
  }

  /**
   * Map new budget types to legacy budget range
   */
  private mapBudgetToBudgetRange(budget: string): BudgetRange {
    if (budget === 'budget') return 'low';
    if (budget === 'midrange' || budget === 'comfortable') return 'medium';
    if (budget === 'luxury') return 'high';
    return 'medium';
  }

  /**
   * Map companions type to legacy travel style
   */
  private mapCompanionsToTravelStyle(companions: string): TravelStyle {
    if (companions === 'solo') return 'solo';
    if (companions === 'couple') return 'couple';
    return 'group'; // family_kids, family_adults, friends
  }
}
