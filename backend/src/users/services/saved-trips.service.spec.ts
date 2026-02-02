import { Test, TestingModule } from '@nestjs/testing';
import { SavedTripsService } from './saved-trips.service';
import { SavedTrip } from '../entities/saved-trip.entity';
import { Repository } from 'typeorm';
import { getRepositoryToken } from '@nestjs/typeorm';
import { NotFoundException } from '@nestjs/common';

describe('SavedTripsService', () => {
  let service: SavedTripsService;
  let repository: Repository<SavedTrip>;

  const mockRepository = {
    create: jest.fn(),
    save: jest.fn(),
    find: jest.fn(),
    findOne: jest.fn(),
    remove: jest.fn(),
    count: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        SavedTripsService,
        {
          provide: getRepositoryToken(SavedTrip),
          useValue: mockRepository,
        },
      ],
    }).compile();

    service = module.get<SavedTripsService>(SavedTripsService);
    repository = module.get<Repository<SavedTrip>>(
      getRepositoryToken(SavedTrip),
    );
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('saveTrip', () => {
    it('should create and save a new trip', async () => {
      const userId = 'user-123';
      const createDto = {
        name: 'Test Trip',
        itinerary_data: { days: [] },
        notes: 'Test notes',
      };

      const savedTrip = {
        id: 'trip-123',
        user_id: userId,
        ...createDto,
        created_at: new Date(),
        updated_at: new Date(),
      };

      mockRepository.create.mockReturnValue(savedTrip);
      mockRepository.save.mockResolvedValue(savedTrip);

      const result = await service.saveTrip(userId, createDto);

      expect(mockRepository.create).toHaveBeenCalledWith({
        user_id: userId,
        name: createDto.name,
        itinerary_data: createDto.itinerary_data,
        notes: createDto.notes,
      });
      expect(mockRepository.save).toHaveBeenCalledWith(savedTrip);
      expect(result).toEqual(savedTrip);
    });
  });

  describe('getSavedTrips', () => {
    it('should return all saved trips for a user', async () => {
      const userId = 'user-123';
      const trips = [
        {
          id: 'trip-1',
          user_id: userId,
          name: 'Trip 1',
          itinerary_data: {},
          notes: null,
          created_at: new Date(),
          updated_at: new Date(),
        },
        {
          id: 'trip-2',
          user_id: userId,
          name: 'Trip 2',
          itinerary_data: {},
          notes: null,
          created_at: new Date(),
          updated_at: new Date(),
        },
      ];

      mockRepository.find.mockResolvedValue(trips);

      const result = await service.getSavedTrips(userId);

      expect(mockRepository.find).toHaveBeenCalledWith({
        where: { user_id: userId },
        order: { created_at: 'DESC' },
      });
      expect(result).toEqual(trips);
    });
  });

  describe('getSavedTripById', () => {
    it('should return a trip if found', async () => {
      const userId = 'user-123';
      const tripId = 'trip-123';
      const trip = {
        id: tripId,
        user_id: userId,
        name: 'Test Trip',
        itinerary_data: {},
        notes: null,
        created_at: new Date(),
        updated_at: new Date(),
      };

      mockRepository.findOne.mockResolvedValue(trip);

      const result = await service.getSavedTripById(userId, tripId);

      expect(mockRepository.findOne).toHaveBeenCalledWith({
        where: { id: tripId, user_id: userId },
      });
      expect(result).toEqual(trip);
    });

    it('should throw NotFoundException if trip not found', async () => {
      const userId = 'user-123';
      const tripId = 'trip-123';

      mockRepository.findOne.mockResolvedValue(null);

      await expect(service.getSavedTripById(userId, tripId)).rejects.toThrow(
        NotFoundException,
      );
    });
  });

  describe('updateSavedTrip', () => {
    it('should update a trip', async () => {
      const userId = 'user-123';
      const tripId = 'trip-123';
      const existingTrip = {
        id: tripId,
        user_id: userId,
        name: 'Old Name',
        itinerary_data: { old: 'data' },
        notes: 'Old notes',
        created_at: new Date(),
        updated_at: new Date(),
      };

      const updateDto = {
        name: 'New Name',
        notes: 'New notes',
      };

      mockRepository.findOne.mockResolvedValue(existingTrip);
      mockRepository.save.mockResolvedValue({
        ...existingTrip,
        ...updateDto,
      });

      const result = await service.updateSavedTrip(userId, tripId, updateDto);

      expect(result.name).toBe('New Name');
      expect(result.notes).toBe('New notes');
      expect(mockRepository.save).toHaveBeenCalled();
    });
  });

  describe('deleteSavedTrip', () => {
    it('should delete a trip', async () => {
      const userId = 'user-123';
      const tripId = 'trip-123';
      const trip = {
        id: tripId,
        user_id: userId,
        name: 'Test Trip',
        itinerary_data: {},
        notes: null,
        created_at: new Date(),
        updated_at: new Date(),
      };

      mockRepository.findOne.mockResolvedValue(trip);
      mockRepository.remove.mockResolvedValue(trip);

      await service.deleteSavedTrip(userId, tripId);

      expect(mockRepository.remove).toHaveBeenCalledWith(trip);
    });
  });

  describe('getSavedTripsCount', () => {
    it('should return the count of saved trips', async () => {
      const userId = 'user-123';
      mockRepository.count.mockResolvedValue(5);

      const result = await service.getSavedTripsCount(userId);

      expect(mockRepository.count).toHaveBeenCalledWith({
        where: { user_id: userId },
      });
      expect(result).toBe(5);
    });
  });
});
