import { IsEnum, IsBoolean } from 'class-validator';

export class SubmitUserOnboardingDto {
  @IsEnum(['short', 'medium', 'long', 'extended'], {
    message: 'duration must be one of: short, medium, long, extended',
  })
  duration: string;

  @IsEnum(['solo', 'couple', 'family_kids', 'family_adults', 'friends'], {
    message:
      'companions must be one of: solo, couple, family_kids, family_adults, friends',
  })
  companions: string;

  @IsEnum(['budget', 'midrange', 'comfortable', 'luxury'], {
    message: 'budget must be one of: budget, midrange, comfortable, luxury',
  })
  budget: string;

  @IsEnum(['slow', 'balanced', 'fast'], {
    message: 'pace must be one of: slow, balanced, fast',
  })
  pace: string;

  @IsEnum(
    ['adventure', 'cultural', 'nature', 'food', 'wellness', 'photography'],
    {
      message:
        'travelStyle must be one of: adventure, cultural, nature, food, wellness, photography',
    },
  )
  travelStyle: string;

  @IsEnum(['low', 'medium', 'high'], {
    message: 'activity must be one of: low, medium, high',
  })
  activity: string;

  @IsEnum(['avoid', 'mixed', 'embrace'], {
    message: 'crowds must be one of: avoid, mixed, embrace',
  })
  crowds: string;

  @IsEnum(['hostel', 'standard', 'boutique', 'premium'], {
    message:
      'accommodation must be one of: hostel, standard, boutique, premium',
  })
  accommodation: string;

  @IsBoolean({
    message: 'remote must be a boolean',
  })
  remote: boolean;

  @IsEnum(['morning', 'flexible', 'evening'], {
    message: 'timing must be one of: morning, flexible, evening',
  })
  timing: string;
}
