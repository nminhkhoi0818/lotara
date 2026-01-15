import { Test, TestingModule } from '@nestjs/testing';
import { UsersService } from '../services/users.service';
import { VibeMappingService } from '../services/vibe-mapping.service';

describe('UsersService', () => {
  let service: UsersService;
  let vibeMappingService: VibeMappingService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [UsersService, VibeMappingService],
    }).compile();

    service = module.get<UsersService>(UsersService);
    vibeMappingService = module.get<VibeMappingService>(VibeMappingService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('createUserFromOnboarding', () => {
    it('should create a user and return userId', () => {
      const dto = {
        budget: 'medium',
        travelStyle: 'solo',
        answers: {
          quiet_or_lively: 'quiet',
          nature_or_city: 'nature',
          crowd_tolerance: 3,
        },
      };

      const userId = service.createUserFromOnboarding(dto);

      expect(userId).toBeDefined();
      expect(typeof userId).toBe('string');
      expect(userId.length).toBeGreaterThan(0);
    });

    it('should persist user data', () => {
      const dto = {
        budget: 'low',
        travelStyle: 'couple',
        answers: {
          quiet_or_lively: 'lively',
          nature_or_city: 'city',
          crowd_tolerance: 8,
        },
      };

      const userId = service.createUserFromOnboarding(dto);
      const user = service.getUserById(userId);

      expect(user).toBeDefined();
      expect(user!.id).toBe(userId);
      expect(user!.budget_range).toBe('low');
      expect(user!.travel_style).toBe('couple');
    });

    it('should map vibe vector correctly', () => {
      const dto = {
        budget: 'high',
        travelStyle: 'group',
        answers: {
          quiet_or_lively: 'quiet',
          nature_or_city: 'nature',
          crowd_tolerance: 4,
        },
      };

      const userId = service.createUserFromOnboarding(dto);
      const user = service.getUserById(userId);

      expect(user).toBeDefined();
      expect(user!.vibe_vector.lowkey).toBe(8);
      expect(user!.vibe_vector.social).toBe(3);
      expect(user!.vibe_vector.nature).toBe(9);
      expect(user!.vibe_vector.crowds).toBe(4);
    });

    it('should set created_at timestamp', () => {
      const beforeCreation = new Date();

      const dto = {
        budget: 'medium',
        travelStyle: 'solo',
        answers: {},
      };

      const userId = service.createUserFromOnboarding(dto);
      const user = service.getUserById(userId);

      const afterCreation = new Date();

      expect(user).toBeDefined();
      expect(user!.created_at).toBeInstanceOf(Date);
      expect(user!.created_at.getTime()).toBeGreaterThanOrEqual(
        beforeCreation.getTime(),
      );
      expect(user!.created_at.getTime()).toBeLessThanOrEqual(
        afterCreation.getTime(),
      );
    });
  });

  describe('getUserById', () => {
    it('should return undefined for non-existent user', () => {
      const user = service.getUserById('non-existent-id');
      expect(user).toBeUndefined();
    });
  });

  describe('getAllUsers', () => {
    it('should return empty array initially', () => {
      const users = service.getAllUsers();
      expect(users).toEqual([]);
    });

    it('should return all created users', () => {
      const dto1 = {
        budget: 'low',
        travelStyle: 'solo',
        answers: {},
      };

      const dto2 = {
        budget: 'high',
        travelStyle: 'group',
        answers: {},
      };

      service.createUserFromOnboarding(dto1);
      service.createUserFromOnboarding(dto2);

      const users = service.getAllUsers();
      expect(users).toHaveLength(2);
    });
  });
});
