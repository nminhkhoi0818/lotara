import {
  Injectable,
  NotFoundException,
  BadRequestException,
} from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { SavedTrip } from '../entities/saved-trip.entity';
import { CreateSavedTripDto, UpdateSavedTripDto } from '../dto/saved-trip.dto';

/**
 * Service for managing user's saved trips.
 */
@Injectable()
export class SavedTripsService {
  constructor(
    @InjectRepository(SavedTrip)
    private savedTripsRepository: Repository<SavedTrip>,
  ) {}

  /**
   * Save a new trip for a user.
   *
   * @param userId User ID
   * @param createDto Trip data to save
   * @returns Created saved trip
   */
  async saveTrip(
    userId: string,
    createDto: CreateSavedTripDto,
  ): Promise<SavedTrip> {
    const savedTrip = this.savedTripsRepository.create({
      user_id: userId,
      name: createDto.name,
      itinerary_data: createDto.itinerary_data,
      notes: createDto.notes,
    });

    return await this.savedTripsRepository.save(savedTrip);
  }

  /**
   * Get all saved trips for a user.
   *
   * @param userId User ID
   * @returns Array of saved trips
   */
  async getSavedTrips(userId: string): Promise<SavedTrip[]> {
    return await this.savedTripsRepository.find({
      where: { user_id: userId },
      order: { created_at: 'DESC' },
    });
  }

  /**
   * Get a specific saved trip by ID.
   *
   * @param userId User ID
   * @param tripId Trip ID
   * @returns Saved trip
   * @throws NotFoundException if trip not found or doesn't belong to user
   */
  async getSavedTripById(userId: string, tripId: string): Promise<SavedTrip> {
    const trip = await this.savedTripsRepository.findOne({
      where: { id: tripId, user_id: userId },
    });

    if (!trip) {
      throw new NotFoundException(
        `Saved trip ${tripId} not found or doesn't belong to user ${userId}`,
      );
    }

    return trip;
  }

  /**
   * Update a saved trip.
   *
   * @param userId User ID
   * @param tripId Trip ID
   * @param updateDto Updated trip data
   * @returns Updated saved trip
   * @throws NotFoundException if trip not found or doesn't belong to user
   */
  async updateSavedTrip(
    userId: string,
    tripId: string,
    updateDto: UpdateSavedTripDto,
  ): Promise<SavedTrip> {
    const trip = await this.getSavedTripById(userId, tripId);

    if (updateDto.name !== undefined) {
      trip.name = updateDto.name;
    }
    if (updateDto.itinerary_data !== undefined) {
      trip.itinerary_data = updateDto.itinerary_data;
    }
    if (updateDto.notes !== undefined) {
      trip.notes = updateDto.notes;
    }

    return await this.savedTripsRepository.save(trip);
  }

  /**
   * Delete a saved trip.
   *
   * @param userId User ID
   * @param tripId Trip ID
   * @throws NotFoundException if trip not found or doesn't belong to user
   */
  async deleteSavedTrip(userId: string, tripId: string): Promise<void> {
    const trip = await this.getSavedTripById(userId, tripId);
    await this.savedTripsRepository.remove(trip);
  }

  /**
   * Get count of saved trips for a user.
   *
   * @param userId User ID
   * @returns Number of saved trips
   */
  async getSavedTripsCount(userId: string): Promise<number> {
    return await this.savedTripsRepository.count({
      where: { user_id: userId },
    });
  }
}
