import { Injectable, Logger, HttpException, HttpStatus } from '@nestjs/common';
import axios, { AxiosError } from 'axios';

export interface AIItineraryRequest {
  userId: string;
  duration: string;
  companions: string;
  budget: string;
  pace: string;
  travelStyle: string;
  activity: string;
  crowds: string;
  accommodation: string;
  remote: boolean;
  timing: string;
}

export interface AIItineraryResponse {
  // The AI service will return its own structure
  // We'll return it as-is to the frontend
  [key: string]: any;
}

/**
 * Service for integrating with the AI itinerary generation service.
 */
@Injectable()
export class AIIntegrationService {
  private readonly logger = new Logger(AIIntegrationService.name);
  private readonly AI_SERVICE_URL =
    'https://testlotara.zeabur.app/api/itinerary/generate';

  /**
   * Generates an itinerary by calling the AI service with user preferences.
   *
   * @param request User preferences and persona data
   * @returns AI-generated itinerary response
   * @throws HttpException if the AI service call fails
   */
  async generateItinerary(
    request: AIItineraryRequest,
  ): Promise<AIItineraryResponse> {
    try {
      this.logger.log(`Calling AI service for user: ${request.userId}`);
      this.logger.debug(`Request data: ${JSON.stringify(request, null, 2)}`);

      const response = await axios.post<AIItineraryResponse>(
        this.AI_SERVICE_URL,
        request,
        {
          headers: {
            'Content-Type': 'application/json',
          },
          timeout: 600000, // 600 second timeout for AI generation
        },
      );

      this.logger.log(
        `AI service responded successfully for user: ${request.userId}`,
      );
      return response.data;
    } catch (error) {
      this.logger.error(
        `AI service call failed for user: ${request.userId}`,
        error,
      );

      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError;

        if (axiosError.response) {
          // The AI service responded with an error status
          this.logger.error(
            `AI service error response: ${JSON.stringify(axiosError.response.data)}`,
          );
          throw new HttpException(
            {
              message: 'AI service returned an error',
              error: axiosError.response.data,
              statusCode: axiosError.response.status,
            },
            axiosError.response.status,
          );
        } else if (axiosError.request) {
          // The request was made but no response received
          this.logger.error('No response received from AI service');
          throw new HttpException(
            {
              message: 'AI service did not respond',
              error:
                'No response received from the AI service. Please try again later.',
            },
            HttpStatus.SERVICE_UNAVAILABLE,
          );
        }
      }

      // Unknown error
      throw new HttpException(
        {
          message: 'Failed to generate itinerary',
          error:
            error instanceof Error ? error.message : 'Unknown error occurred',
        },
        HttpStatus.INTERNAL_SERVER_ERROR,
      );
    }
  }
}
