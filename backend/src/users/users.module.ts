import { Module } from '@nestjs/common';
import { UsersController } from './controllers/users.controller';
import { UsersService } from './services/users.service';
import { VibeMappingService } from './services/vibe-mapping.service';

@Module({
  controllers: [UsersController],
  providers: [UsersService, VibeMappingService],
  exports: [UsersService, VibeMappingService],
})
export class UsersModule {}
