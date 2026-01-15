import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication, ValidationPipe } from '@nestjs/common';
import * as request from 'supertest';
import { UsersController } from './controllers/users.controller';
import { UsersService } from './services/users.service';
import { VibeMappingService } from './services/vibe-mapping.service';

describe('UsersController - Onboarding (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      controllers: [UsersController],
      providers: [UsersService, VibeMappingService],
    }).compile();

    app = moduleFixture.createNestApplication();
    app.useGlobalPipes(
      new ValidationPipe({
        whitelist: true,
        forbidNonWhitelisted: true,
        transform: true,
        transformOptions: {
          enableImplicitConversion: true,
        },
      }),
    );
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  describe('POST /users/onboarding', () => {
    it('should onboard a user successfully with valid input', () => {
      const payload = {
        budget: 'medium',
        travelStyle: 'solo',
        answers: {
          quiet_or_lively: 'quiet',
          nature_or_city: 'nature',
          crowd_tolerance: 3,
        },
      };

      return request(app.getHttpServer())
        .post('/users/onboarding')
        .send(payload)
        .expect(201)
        .expect((res) => {
          expect(res.body).toHaveProperty('userId');
          expect(typeof res.body.userId).toBe('string');
          expect(res.body.userId.length).toBeGreaterThan(0);
        });
    });

    it('should reject invalid budget', () => {
      const payload = {
        budget: 'invalid',
        travelStyle: 'solo',
        answers: {
          quiet_or_lively: 'quiet',
        },
      };

      return request(app.getHttpServer())
        .post('/users/onboarding')
        .send(payload)
        .expect(400);
    });

    it('should reject invalid travelStyle', () => {
      const payload = {
        budget: 'medium',
        travelStyle: 'invalid',
        answers: {
          quiet_or_lively: 'quiet',
        },
      };

      return request(app.getHttpServer())
        .post('/users/onboarding')
        .send(payload)
        .expect(400);
    });

    it('should reject invalid quiet_or_lively', () => {
      const payload = {
        budget: 'medium',
        travelStyle: 'solo',
        answers: {
          quiet_or_lively: 'invalid',
        },
      };

      return request(app.getHttpServer())
        .post('/users/onboarding')
        .send(payload)
        .expect(400);
    });

    it('should reject invalid nature_or_city', () => {
      const payload = {
        budget: 'medium',
        travelStyle: 'solo',
        answers: {
          nature_or_city: 'invalid',
        },
      };

      return request(app.getHttpServer())
        .post('/users/onboarding')
        .send(payload)
        .expect(400);
    });

    it('should reject crowd_tolerance out of range', () => {
      const payload = {
        budget: 'medium',
        travelStyle: 'solo',
        answers: {
          crowd_tolerance: 11,
        },
      };

      return request(app.getHttpServer())
        .post('/users/onboarding')
        .send(payload)
        .expect(400);
    });

    it('should accept empty answers', () => {
      const payload = {
        budget: 'medium',
        travelStyle: 'solo',
        answers: {},
      };

      return request(app.getHttpServer())
        .post('/users/onboarding')
        .send(payload)
        .expect(201)
        .expect((res) => {
          expect(res.body).toHaveProperty('userId');
        });
    });

    it('should accept partial answers', () => {
      const payload = {
        budget: 'high',
        travelStyle: 'couple',
        answers: {
          quiet_or_lively: 'lively',
          crowd_tolerance: 7,
        },
      };

      return request(app.getHttpServer())
        .post('/users/onboarding')
        .send(payload)
        .expect(201)
        .expect((res) => {
          expect(res.body).toHaveProperty('userId');
        });
    });

    it('should handle all budget options', async () => {
      const budgets = ['low', 'medium', 'high'];

      for (const budget of budgets) {
        const payload = {
          budget,
          travelStyle: 'solo',
          answers: {},
        };

        await request(app.getHttpServer())
          .post('/users/onboarding')
          .send(payload)
          .expect(201);
      }
    });

    it('should handle all travelStyle options', async () => {
      const styles = ['solo', 'couple', 'group'];

      for (const style of styles) {
        const payload = {
          budget: 'medium',
          travelStyle: style,
          answers: {},
        };

        await request(app.getHttpServer())
          .post('/users/onboarding')
          .send(payload)
          .expect(201);
      }
    });

    it('should accept crowd_tolerance boundary values', async () => {
      const boundaries = [0, 10];

      for (const value of boundaries) {
        const payload = {
          budget: 'medium',
          travelStyle: 'solo',
          answers: {
            crowd_tolerance: value,
          },
        };

        await request(app.getHttpServer())
          .post('/users/onboarding')
          .send(payload)
          .expect(201);
      }
    });
  });
});
