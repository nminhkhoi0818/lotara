import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ConfigModule } from '@nestjs/config';
import { UsersController } from './controllers/users.controller';
import { UsersService } from './services/users.service';
import { VibeMappingService } from './services/vibe-mapping.service';
import { GeminiService } from './services/gemini.service';
import { User } from './entities/user.entity';

@Module({
  imports: [TypeOrmModule.forFeature([User]), ConfigModule],
  controllers: [UsersController],
  providers: [UsersService, VibeMappingService, GeminiService],
  exports: [UsersService, VibeMappingService],
})
export class UsersModule {}
