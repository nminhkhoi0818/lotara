import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConfigModule } from '@nestjs/config';
import { UsersController } from './controllers/users.controller';
import { SavedTripsController } from './controllers/saved-trips.controller';
import { UsersService } from './services/users.service';
import { VibeMappingService } from './services/vibe-mapping.service';
import { GeminiService } from './services/gemini.service';
import { SavedTripsService } from './services/saved-trips.service';
import { User } from './entities/user.entity';
import { SavedTrip } from './entities/saved-trip.entity';

@Module({
  imports: [TypeOrmModule.forFeature([User, SavedTrip]), ConfigModule],
  controllers: [UsersController, SavedTripsController],
  providers: [
    UsersService,
    VibeMappingService,
    GeminiService,
    SavedTripsService,
  ],
  exports: [UsersService, VibeMappingService, SavedTripsService],
})
export class UsersModule {}
