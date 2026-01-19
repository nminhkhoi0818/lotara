import {
  Controller,
  Post,
  Body,
  BadRequestException,
  InternalServerErrorException,
} from '@nestjs/common';
import { UsersService } from '../services/users.service';
import { CreateUserOnboardingDto } from '../dto/create-user-onboarding.dto';
import { SubmitUserOnboardingDto } from '../dto/submit-user-onboarding.dto';
import { UserOnboardingResponseDto } from '../dto/user-onboarding-response.dto';
import { UserPersonaResponseDto } from '../dto/user-persona-response.dto';

@Controller('users')
export class UsersController {
  constructor(private usersService: UsersService) {}

  /**
   * POST /users/onboarding
   *
   * Creates a new user from onboarding data.
   *
   * Request payload:
   * {
   *   "budget": "medium",
   *   "travelStyle": "solo",
   *   "answers": {
   *     "quiet_or_lively": "quiet",
   *     "nature_or_city": "nature",
   *     "crowd_tolerance": 2
   *   }
   * }
   *
   * Success response (200 OK):
   * {
   *   "userId": "uuid-string"
   * }
   *
   * Error responses:
   * - 400 Bad Request: Invalid input or vibe values
   * - 500 Internal Server Error: Persistence failure
   *
   * @param createUserOnboardingDto Onboarding request
   * @returns User ID
   */
  @Post('onboarding')
  async onboardUser(
    @Body() createUserOnboardingDto: CreateUserOnboardingDto,
  ): Promise<UserOnboardingResponseDto> {
    try {
      const userId = this.usersService.createUserFromOnboarding(
        createUserOnboardingDto,
      );

      return {
        userId,
      };
    } catch (error) {
      // Re-throw BadRequestException for validation errors
      if (error instanceof BadRequestException) {
        throw error;
      }

      // Wrap other errors as internal server errors
      throw new InternalServerErrorException(
        'Failed to process user onboarding',
      );
    }
  }

  /**
   * POST /users/onboarding/submit
   *
   * Submits user onboarding answers from the persona questionnaire.
   *
   * Request payload:
   * {
   *   "duration": "medium",
   *   "companions": "solo",
   *   "budget": "midrange",
   *   "pace": "balanced",
   *   "travelStyle": "cultural",
   *   "activity": "medium",
   *   "crowds": "mixed",
   *   "accommodation": "standard",
   *   "remote": false,
   *   "timing": "flexible"
   * }
   *
   * Success response (200 OK):
   * {
   *   "userId": "uuid-string",
   *   "duration": "medium",
   *   "companions": "solo",
   *   "budget": "midrange",
   *   "pace": "balanced",
   *   "travelStyle": "cultural",
   *   "activity": "medium",
   *   "crowds": "mixed",
   *   "accommodation": "standard",
   *   "remote": false,
   *   "timing": "flexible"
   * }
   *
   * Error responses:
   * - 400 Bad Request: Invalid input
   * - 500 Internal Server Error: Persistence failure
   *
   * @param submitUserOnboardingDto Persona questionnaire answers
   * @returns User persona data with userId
   */
  @Post('onboarding/submit')
  async submitOnboarding(
    @Body() submitUserOnboardingDto: SubmitUserOnboardingDto,
  ): Promise<UserPersonaResponseDto> {
    try {
      const user = this.usersService.submitUserOnboarding(
        submitUserOnboardingDto,
      );

      // Return the persona data along with userId
      return {
        userId: user.id,
        duration: user.persona_answers!.duration,
        companions: user.persona_answers!.companions,
        budget: user.persona_answers!.budget,
        pace: user.persona_answers!.pace,
        travelStyle: user.persona_answers!.travelStyle,
        activity: user.persona_answers!.activity,
        crowds: user.persona_answers!.crowds,
        accommodation: user.persona_answers!.accommodation,
        remote: user.persona_answers!.remote,
        timing: user.persona_answers!.timing,
      };
    } catch (error) {
      // Re-throw BadRequestException for validation errors
      if (error instanceof BadRequestException) {
        throw error;
      }

      // Wrap other errors as internal server errors
      throw new InternalServerErrorException(
        'Failed to submit user onboarding',
      );
    }
  }
}
