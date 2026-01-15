import {
  Controller,
  Post,
  Body,
  BadRequestException,
  InternalServerErrorException,
} from '@nestjs/common';
import { UsersService } from '../services/users.service';
import { CreateUserOnboardingDto } from '../dto/create-user-onboarding.dto';
import { UserOnboardingResponseDto } from '../dto/user-onboarding-response.dto';

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
}
