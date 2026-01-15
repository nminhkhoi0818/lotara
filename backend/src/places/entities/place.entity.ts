import {
  VibeVector,
  BudgetRange,
  TravelStyle,
} from '../../users/entities/user.entity';

export class Place {
  id: string;
  name: string;
  region: string;
  description: string;
  vibe_vector: VibeVector;
  budget_range: BudgetRange;
  travel_style: TravelStyle;
  image_url?: string;

  constructor(
    id: string,
    name: string,
    region: string,
    description: string,
    vibe_vector: VibeVector,
    budget_range: BudgetRange,
    travel_style: TravelStyle,
    image_url?: string,
  ) {
    this.id = id;
    this.name = name;
    this.region = region;
    this.description = description;
    this.vibe_vector = vibe_vector;
    this.budget_range = budget_range;
    this.travel_style = travel_style;
    this.image_url = image_url;
  }
}
