import {
  IsEnum,
  IsObject,
  ValidateNested,
  IsNumber,
  Min,
  Max,
  IsOptional,
} from 'class-validator';
import { Type } from 'class-transformer';

export class OnboardingAnswersDto {
  @IsOptional()
  @IsEnum(['quiet', 'lively'], {
    message: 'quiet_or_lively must be either "quiet" or "lively"',
  })
  quiet_or_lively?: string;

  @IsOptional()
  @IsEnum(['nature', 'city'], {
    message: 'nature_or_city must be either "nature" or "city"',
  })
  nature_or_city?: string;

  @IsOptional()
  @IsNumber()
  @Min(0, { message: 'crowd_tolerance must be between 0 and 10' })
  @Max(10, { message: 'crowd_tolerance must be between 0 and 10' })
  crowd_tolerance?: number;
}

export class CreateUserOnboardingDto {
  @IsEnum(['low', 'medium', 'high'], {
    message: 'budget must be one of: low, medium, high',
  })
  budget: string;

  @IsEnum(['solo', 'couple', 'group'], {
    message: 'travelStyle must be one of: solo, couple, group',
  })
  travelStyle: string;

  @ValidateNested()
  @Type(() => OnboardingAnswersDto)
  @IsObject({
    message: 'answers must be an object',
  })
  answers: OnboardingAnswersDto;
}
