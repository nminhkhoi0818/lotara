import { Module } from '@nestjs/common';
import { UsersModule } from '../users/users.module';
import { PlacesModule } from '../places/places.module';
import { RecommendationsController } from './controllers/recommendations.controller';
import { RecommendationsService } from './services/recommendations.service';
import { MatchScoringService } from './services/match-scoring.service';
import { AIIntegrationService } from './services/ai-integration.service';

@Module({
  imports: [UsersModule, PlacesModule],
  controllers: [RecommendationsController],
  providers: [
    RecommendationsService,
    MatchScoringService,
    AIIntegrationService,
  ],
  exports: [RecommendationsService, MatchScoringService],
})
export class RecommendationsModule {}
