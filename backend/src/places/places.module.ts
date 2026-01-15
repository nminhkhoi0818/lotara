import { Module } from '@nestjs/common';
import { PlacesService } from './services/places.service';

@Module({
  providers: [PlacesService],
  exports: [PlacesService],
})
export class PlacesModule {}
