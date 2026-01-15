import { Module } from '@nestjs/common';
import { UsersModule } from '../users/users.module';
import { PlacesModule } from '../places/places.module';
import { RecommendationsController } from './controllers/recommendations.controller';
import { RecommendationsService } from './services/recommendations.service';
import { MatchScoringService } from './services/match-scoring.service';

@Module({
  imports: [UsersModule, PlacesModule],
  controllers: [RecommendationsController],
  providers: [RecommendationsService, MatchScoringService],
  exports: [RecommendationsService, MatchScoringService],
})
export class RecommendationsModule {}
