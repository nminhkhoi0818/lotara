import { v4 as uuidv4 } from 'uuid';

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

export class User {
  id: string;
  vibe_vector: VibeVector;
  budget_range: BudgetRange;
  travel_style: TravelStyle;
  persona_answers?: PersonaAnswers;
  created_at: Date;

  constructor(
    vibe_vector: VibeVector,
    budget_range: BudgetRange,
    travel_style: TravelStyle,
    persona_answers?: PersonaAnswers,
  ) {
    this.id = uuidv4();
    this.vibe_vector = vibe_vector;
    this.budget_range = budget_range;
    this.travel_style = travel_style;
    this.persona_answers = persona_answers;
    this.created_at = new Date();
  }
}
