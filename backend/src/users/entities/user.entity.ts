import { v4 as uuidv4 } from 'uuid';

export type BudgetRange = 'low' | 'medium' | 'high';
export type TravelStyle = 'solo' | 'couple' | 'group';

export interface VibeVector {
  lowkey: number;
  nature: number;
  crowds: number;
  social: number;
}

export class User {
  id: string;
  vibe_vector: VibeVector;
  budget_range: BudgetRange;
  travel_style: TravelStyle;
  created_at: Date;

  constructor(
    vibe_vector: VibeVector,
    budget_range: BudgetRange,
    travel_style: TravelStyle,
  ) {
    this.id = uuidv4();
    this.vibe_vector = vibe_vector;
    this.budget_range = budget_range;
    this.travel_style = travel_style;
    this.created_at = new Date();
  }
}
