import { Injectable } from '@nestjs/common';
import { Place } from '../entities/place.entity';

/**
 * Service that provides a mock dataset of Vietnam travel places.
 * Each place has a vibe vector for matching against user preferences.
 */
@Injectable()
export class PlacesService {
  private places: Map<string, Place> = new Map();

  constructor() {
    this.initializeMockPlaces();
  }

  /**
   * Initializes the mock dataset with Vietnamese travel destinations.
   * Real implementation would load from database.
   */
  private initializeMockPlaces(): void {
    const mockPlaces: Place[] = [
      new Place(
        'place-1',
        'Halong Bay',
        'Quang Ninh',
        'Stunning limestone karst formations in the Gulf of Tonkin. UNESCO World Heritage site.',
        { lowkey: 6, nature: 9, crowds: 7, social: 5 },
        'high',
        'group',
        'https://example.com/halong-bay.jpg',
      ),
      new Place(
        'place-2',
        'Hoi An Ancient Town',
        'Quang Nam',
        'Charming riverside town with well-preserved architecture and lantern-lit streets.',
        { lowkey: 7, nature: 5, crowds: 8, social: 8 },
        'high',
        'couple',
        'https://example.com/hoi-an.jpg',
      ),
      new Place(
        'place-3',
        'Sapa',
        'Lao Cai',
        'Mountain town known for trekking, rice terraces, and hill tribe villages.',
        { lowkey: 8, nature: 9, crowds: 4, social: 4 },
        'medium',
        'solo',
        'https://example.com/sapa.jpg',
      ),
      new Place(
        'place-4',
        'Ho Chi Minh City',
        'Ho Chi Minh City',
        'Vibrant metropolis with markets, temples, museums, and bustling nightlife.',
        { lowkey: 2, nature: 3, crowds: 9, social: 9 },
        'high',
        'group',
        'https://example.com/hcmc.jpg',
      ),
      new Place(
        'place-5',
        'Da Nang Beaches',
        'Da Nang',
        'Beautiful coastal city with pristine beaches and water sports opportunities.',
        { lowkey: 5, nature: 8, crowds: 6, social: 6 },
        'medium',
        'couple',
        'https://example.com/danang.jpg',
      ),
      new Place(
        'place-6',
        'Hanoi Old Quarter',
        'Hanoi',
        'Historic district with narrow streets, street food, and centuries-old architecture.',
        { lowkey: 3, nature: 2, crowds: 9, social: 8 },
        'medium',
        'solo',
        'https://example.com/hanoi-old-quarter.jpg',
      ),
      new Place(
        'place-7',
        'Mekong Delta',
        'Can Tho',
        'Peaceful river delta with floating markets, fruit orchards, and local culture.',
        { lowkey: 8, nature: 8, crowds: 5, social: 5 },
        'low',
        'couple',
        'https://example.com/mekong.jpg',
      ),
      new Place(
        'place-8',
        'Cat Ba Island',
        'Hai Phong',
        'Adventure destination with rock climbing, hiking, and beautiful coastal views.',
        { lowkey: 6, nature: 8, crowds: 5, social: 6 },
        'medium',
        'solo',
        'https://example.com/cat-ba.jpg',
      ),
      new Place(
        'place-9',
        'Bali-style Nha Trang',
        'Khanh Hoa',
        'Beach resort town with islands, temples, and water activities.',
        { lowkey: 5, nature: 7, crowds: 7, social: 7 },
        'high',
        'couple',
        'https://example.com/nha-trang.jpg',
      ),
      new Place(
        'place-10',
        'Phong Nha Cave',
        'Quang Binh',
        'Remote cave system with underground rivers and pristine jungle environment.',
        { lowkey: 9, nature: 10, crowds: 2, social: 2 },
        'low',
        'solo',
        'https://example.com/phong-nha.jpg',
      ),
      new Place(
        'place-11',
        'Dalat Highlands',
        'Lam Dong',
        'Cool-climate town with waterfalls, pine forests, and French colonial architecture.',
        { lowkey: 7, nature: 8, crowds: 3, social: 4 },
        'low',
        'couple',
        'https://example.com/dalat.jpg',
      ),
      new Place(
        'place-12',
        'Hanoi Cycling Tour',
        'Hanoi',
        'Guided cycling adventure through rural villages and rice paddies near Hanoi.',
        { lowkey: 6, nature: 7, crowds: 3, social: 7 },
        'medium',
        'solo',
        'https://example.com/cycling-tour.jpg',
      ),
    ];

    mockPlaces.forEach((place) => this.places.set(place.id, place));
  }

  /**
   * Get a place by ID.
   *
   * @param placeId Place ID
   * @returns Place or undefined
   */
  getPlaceById(placeId: string): Place | undefined {
    return this.places.get(placeId);
  }

  /**
   * Get all places.
   *
   * @returns Array of all places
   */
  getAllPlaces(): Place[] {
    return Array.from(this.places.values());
  }

  /**
   * Filter places by budget and travel style.
   *
   * @param budget Budget range
   * @param travelStyle Travel style
   * @returns Filtered places
   */
  filterPlacesByPreferences(
    budget: 'low' | 'medium' | 'high',
    travelStyle: 'solo' | 'couple' | 'group',
  ): Place[] {
    return this.getAllPlaces().filter(
      (place) =>
        place.budget_range === budget && place.travel_style === travelStyle,
    );
  }
}
