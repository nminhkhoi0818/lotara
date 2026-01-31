import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
} from 'typeorm';

export type BudgetRange = 'low' | 'medium' | 'high';
export type TravelStyle = 'solo' | 'couple' | 'group';

export interface VibeVector {
  lowkey: number;
  nature: number;
  crowds: number;
  social: number;
}

// New persona types based on frontend
export type Duration = 'short' | 'medium' | 'long' | 'extended';
export type Companions =
  | 'solo'
  | 'couple'
  | 'family_kids'
  | 'family_adults'
  | 'friends';
export type Budget = 'budget' | 'midrange' | 'comfortable' | 'luxury';
export type Pace = 'slow' | 'balanced' | 'fast';
export type TravelStyleNew =
  | 'adventure'
  | 'cultural'
  | 'nature'
  | 'food'
  | 'wellness'
  | 'photography';
export type Activity = 'low' | 'medium' | 'high';
export type Crowds = 'avoid' | 'mixed' | 'embrace';
export type Accommodation = 'hostel' | 'standard' | 'boutique' | 'premium';
export type Timing = 'morning' | 'flexible' | 'evening';

export interface PersonaAnswers {
  duration: Duration;
  companions: Companions;
  budget: Budget;
  pace: Pace;
  travelStyle: TravelStyleNew;
  activity: Activity;
  crowds: Crowds;
  accommodation: Accommodation;
  remote: boolean;
  timing: Timing;
}

@Entity('users')
export class User {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column('jsonb')
  vibe_vector: VibeVector;

  @Column({
    type: 'varchar',
    length: 50,
  })
  budget_range: BudgetRange;

  @Column({
    type: 'varchar',
    length: 50,
  })
  travel_style: TravelStyle;

  @Column('jsonb', { nullable: true })
  persona_answers?: PersonaAnswers;

  @CreateDateColumn()
  created_at: Date;
}
