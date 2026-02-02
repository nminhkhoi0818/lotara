import { IsString, IsNotEmpty, IsOptional, IsObject } from 'class-validator';

export class CreateSavedTripDto {
  @IsString()
  @IsNotEmpty()
  name: string;

  @IsObject()
  @IsNotEmpty()
  itinerary_data: any;

  @IsString()
  @IsOptional()
  notes?: string;
}

export class UpdateSavedTripDto {
  @IsString()
  @IsOptional()
  name?: string;

  @IsObject()
  @IsOptional()
  itinerary_data?: any;

  @IsString()
  @IsOptional()
  notes?: string;
}
