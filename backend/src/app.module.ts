import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { UsersModule } from './users/users.module';
import { RecommendationsModule } from './recommendations/recommendations.module';
import { PlacesModule } from './places/places.module';

@Module({
  imports: [UsersModule, RecommendationsModule, PlacesModule],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
