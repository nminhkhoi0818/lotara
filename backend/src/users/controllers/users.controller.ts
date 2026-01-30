import {
  Controller,
  Post,
  Get,
  Param,
  Body,
  BadRequestException,
  InternalServerErrorException,
  NotFoundException,
  Res,
  Query,
} from '@nestjs/common';
import { Response } from 'express';
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
      const userId = await this.usersService.createUserFromOnboarding(
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
   * Returns persona data along with an AI-generated welcome message.
   *
   * Query parameters:
   * - stream: Set to 'true' to enable Server-Sent Events streaming for AI message
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
   * Success response (200 OK) - Non-streaming:
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
   *   "timing": "flexible",
   *   "aiMessage": "Welcome! Based on your love for cultural experiences..."
   * }
   *
   * Success response (200 OK) - Streaming (SSE):
   * Stream of events with chunks of data and AI message
   *
   * Error responses:
   * - 400 Bad Request: Invalid input
   * - 500 Internal Server Error: Persistence failure
   *
   * @param submitUserOnboardingDto Persona questionnaire answers
   * @param stream Whether to enable streaming
   * @param res Express response object
   * @returns User persona data with AI message
   */
  @Post('onboarding/submit')
  async submitOnboarding(
    @Body() submitUserOnboardingDto: SubmitUserOnboardingDto,
    @Query('stream') stream?: string,
    @Res({ passthrough: true }) res?: Response,
  ): Promise<UserPersonaResponseDto | void> {
    try {
      const enableStream = stream === 'true';

      if (enableStream && res) {
        // Set up Server-Sent Events (SSE)
        res.setHeader('Content-Type', 'text/event-stream');
        res.setHeader('Cache-Control', 'no-cache');
        res.setHeader('Connection', 'keep-alive');

        const { user, aiMessageStream } =
          await this.usersService.submitUserOnboardingWithAIStream(
            submitUserOnboardingDto,
          );

        // Send user data first
        const userData: UserPersonaResponseDto = {
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

        res.write(
          `data: ${JSON.stringify({ type: 'user', data: userData })}\n\n`,
        );

        // Stream AI message chunks
        try {
          for await (const chunk of aiMessageStream) {
            res.write(
              `data: ${JSON.stringify({ type: 'ai_chunk', data: chunk })}\n\n`,
            );
          }

          // Send completion event
          res.write(`data: ${JSON.stringify({ type: 'complete' })}\n\n`);
        } catch (error) {
          res.write(
            `data: ${JSON.stringify({ type: 'error', data: 'Failed to generate AI message' })}\n\n`,
          );
        }

        res.end();
        return;
      } else {
        // Non-streaming response
        const { user, aiMessage } =
          await this.usersService.submitUserOnboardingWithAI(
            submitUserOnboardingDto,
          );

        // Return the persona data along with userId and AI message
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
          aiMessage: aiMessage,
        };
      }
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

  /**
   * GET /users/:id
   *
   * Retrieves a user by ID with all their data including persona answers.
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
   * - 404 Not Found: User does not exist
   * - 500 Internal Server Error: Database error
   *
   * @param id User ID
   * @returns User persona data
   */
  @Get(':id')
  async getUserById(@Param('id') id: string): Promise<UserPersonaResponseDto> {
    try {
      const user = await this.usersService.getUserById(id);

      if (!user) {
        throw new NotFoundException(`User with ID ${id} not found`);
      }

      // Return the persona data if it exists
      if (user.persona_answers) {
        return {
          userId: user.id,
          duration: user.persona_answers.duration,
          companions: user.persona_answers.companions,
          budget: user.persona_answers.budget,
          pace: user.persona_answers.pace,
          travelStyle: user.persona_answers.travelStyle,
          activity: user.persona_answers.activity,
          crowds: user.persona_answers.crowds,
          accommodation: user.persona_answers.accommodation,
          remote: user.persona_answers.remote,
          timing: user.persona_answers.timing,
        };
      }

      // If no persona_answers, return basic user info
      // Map budget_range and travel_style to persona format
      return {
        userId: user.id,
        duration: 'medium' as any,
        companions: user.travel_style as any,
        budget:
          user.budget_range === 'low'
            ? ('budget' as any)
            : user.budget_range === 'high'
              ? ('luxury' as any)
              : ('midrange' as any),
        pace: 'balanced' as any,
        travelStyle: 'cultural' as any,
        activity: 'medium' as any,
        crowds: 'mixed' as any,
        accommodation: 'standard' as any,
        remote: false,
        timing: 'flexible' as any,
      };
    } catch (error) {
      // Re-throw NotFoundException
      if (error instanceof NotFoundException) {
        throw error;
      }

      // Wrap other errors as internal server errors
      throw new InternalServerErrorException('Failed to retrieve user');
    }
  }
}
