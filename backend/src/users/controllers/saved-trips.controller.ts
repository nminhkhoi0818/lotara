import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Param,
  Body,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { SavedTripsService } from '../services/saved-trips.service';
import { CreateSavedTripDto, UpdateSavedTripDto } from '../dto/saved-trip.dto';

@Controller('users/:userId/saved-trips')
export class SavedTripsController {
  constructor(private savedTripsService: SavedTripsService) {}

  /**
   * POST /users/:userId/saved-trips
   *
   * Save a new trip for a user.
   *
   * Request Body:
   * {
   *   "name": "Summer 2026 Vietnam Adventure",
   *   "itinerary_data": { ... },  // Full itinerary response from AI
   *   "notes": "Optional notes about the trip"
   * }
   *
   * Response:
   * {
   *   "id": "uuid",
   *   "user_id": "uuid",
   *   "name": "Summer 2026 Vietnam Adventure",
   *   "itinerary_data": { ... },
   *   "notes": "Optional notes",
   *   "created_at": "2026-02-02T...",
   *   "updated_at": "2026-02-02T..."
   * }
   *
   * @param userId User ID
   * @param createDto Trip data
   * @returns Created saved trip
   */
  @Post()
  async saveTrip(
    @Param('userId') userId: string,
    @Body() createDto: CreateSavedTripDto,
  ) {
    return await this.savedTripsService.saveTrip(userId, createDto);
  }

  /**
   * GET /users/:userId/saved-trips
   *
   * Get all saved trips for a user.
   *
   * Response:
   * [
   *   {
   *     "id": "uuid",
   *     "user_id": "uuid",
   *     "name": "Summer 2026 Vietnam Adventure",
   *     "itinerary_data": { ... },
   *     "notes": "Optional notes",
   *     "created_at": "2026-02-02T...",
   *     "updated_at": "2026-02-02T..."
   *   },
   *   ...
   * ]
   *
   * @param userId User ID
   * @returns Array of saved trips
   */
  @Get()
  async getSavedTrips(@Param('userId') userId: string) {
    return await this.savedTripsService.getSavedTrips(userId);
  }

  /**
   * GET /users/:userId/saved-trips/:tripId
   *
   * Get a specific saved trip by ID.
   *
   * Response:
   * {
   *   "id": "uuid",
   *   "user_id": "uuid",
   *   "name": "Summer 2026 Vietnam Adventure",
   *   "itinerary_data": { ... },
   *   "notes": "Optional notes",
   *   "created_at": "2026-02-02T...",
   *   "updated_at": "2026-02-02T..."
   * }
   *
   * @param userId User ID
   * @param tripId Trip ID
   * @returns Saved trip
   */
  @Get(':tripId')
  async getSavedTripById(
    @Param('userId') userId: string,
    @Param('tripId') tripId: string,
  ) {
    return await this.savedTripsService.getSavedTripById(userId, tripId);
  }

  /**
   * PUT /users/:userId/saved-trips/:tripId
   *
   * Update a saved trip.
   *
   * Request Body (all fields optional):
   * {
   *   "name": "Updated trip name",
   *   "itinerary_data": { ... },
   *   "notes": "Updated notes"
   * }
   *
   * Response:
   * {
   *   "id": "uuid",
   *   "user_id": "uuid",
   *   "name": "Updated trip name",
   *   "itinerary_data": { ... },
   *   "notes": "Updated notes",
   *   "created_at": "2026-02-02T...",
   *   "updated_at": "2026-02-02T..."
   * }
   *
   * @param userId User ID
   * @param tripId Trip ID
   * @param updateDto Updated trip data
   * @returns Updated saved trip
   */
  @Put(':tripId')
  async updateSavedTrip(
    @Param('userId') userId: string,
    @Param('tripId') tripId: string,
    @Body() updateDto: UpdateSavedTripDto,
  ) {
    return await this.savedTripsService.updateSavedTrip(
      userId,
      tripId,
      updateDto,
    );
  }

  /**
   * DELETE /users/:userId/saved-trips/:tripId
   *
   * Delete a saved trip.
   *
   * @param userId User ID
   * @param tripId Trip ID
   */
  @Delete(':tripId')
  @HttpCode(HttpStatus.NO_CONTENT)
  async deleteSavedTrip(
    @Param('userId') userId: string,
    @Param('tripId') tripId: string,
  ) {
    await this.savedTripsService.deleteSavedTrip(userId, tripId);
  }

  /**
   * GET /users/:userId/saved-trips/count
   *
   * Get the number of saved trips for a user.
   *
   * Response:
   * {
   *   "count": 5
   * }
   *
   * @param userId User ID
   * @returns Count object
   */
  @Get('meta/count')
  async getSavedTripsCount(@Param('userId') userId: string) {
    const count = await this.savedTripsService.getSavedTripsCount(userId);
    return { count };
  }
}
