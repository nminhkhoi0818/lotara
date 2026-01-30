import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { PlacesModule } from './places/places.module';
import { QuestionsModule } from './questions/questions.module';
import { RecommendationsModule } from './recommendations/recommendations.module';
import { UsersModule } from './users/users.module';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true, envFilePath: '.env' }),
    TypeOrmModule.forRootAsync({
      useFactory: () => ({
        type: 'postgres',
        host: process.env.POSTGRES_HOST ?? 'localhost',
        port: Number(process.env.POSTGRES_PORT ?? 5432),
        username: process.env.POSTGRES_USER ?? 'lotara',
        password: process.env.POSTGRES_PASSWORD ?? 'lotara',
        database: process.env.POSTGRES_DB ?? 'lotara',
        autoLoadEntities: true,
        synchronize: false, // Changed to false - use migrations instead
        migrationsRun: true, // Automatically run migrations on startup
      }),
    }),
    UsersModule,
    RecommendationsModule,
    PlacesModule,
    QuestionsModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
