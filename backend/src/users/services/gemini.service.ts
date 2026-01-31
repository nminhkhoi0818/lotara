import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { PersonaAnswers } from '../entities/user.entity';

/**
 * Service for integrating with Google's Gemini AI API.
 * Provides personalized chat messages based on user onboarding data.
 */
@Injectable()
export class GeminiService {
  private genAI: GoogleGenerativeAI;
  private model: any;

  constructor(private configService: ConfigService) {
    const apiKey = this.configService.get<string>('GEMINI_API_KEY');
    if (!apiKey) {
      throw new Error('GEMINI_API_KEY is not configured');
    }
    this.genAI = new GoogleGenerativeAI(apiKey);
    this.model = this.genAI.getGenerativeModel({ model: 'gemini-2.5-flash' });
  }

  /**
   * Generate a personalized welcome message based on user's persona answers.
   *
   * @param personaAnswers User's onboarding responses
   * @returns Promise resolving to AI-generated message
   */
  async generateWelcomeMessage(
    personaAnswers: PersonaAnswers,
  ): Promise<string> {
    const prompt = this.buildPrompt(personaAnswers);

    try {
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      return response.text();
    } catch (error) {
      console.error('Error generating AI response:', error);
      throw new Error('Failed to generate AI welcome message');
    }
  }

  /**
   * Generate a personalized welcome message with streaming support.
   *
   * @param personaAnswers User's onboarding responses
   * @returns AsyncGenerator yielding message chunks
   */
  async *generateWelcomeMessageStream(
    personaAnswers: PersonaAnswers,
  ): AsyncGenerator<string, void, unknown> {
    const prompt = this.buildPrompt(personaAnswers);

    try {
      const result = await this.model.generateContentStream(prompt);

      for await (const chunk of result.stream) {
        const chunkText = chunk.text();
        yield chunkText;
      }
    } catch (error) {
      console.error('Error generating AI response stream:', error);
      throw new Error('Failed to generate AI welcome message stream');
    }
  }

  /**
   * Build a detailed prompt for the AI based on persona answers.
   */
  private buildPrompt(personaAnswers: PersonaAnswers): string {
    return `You are an expert travel personality analyst for Lotara, a travel recommendation platform. A user has completed their travel preferences questionnaire.

Based on their responses, create a concise personality summary (4-5 sentences) that:
1. Describes their travel personality and what type of traveler they are
2. Highlights their key preferences and travel characteristics
3. Captures what makes their travel style unique

User's Travel Profile:
- Duration preference: ${personaAnswers.duration} trips
- Traveling with: ${personaAnswers.companions}
- Budget: ${personaAnswers.budget}
- Pace: ${personaAnswers.pace} pace
- Travel style: ${personaAnswers.travelStyle}
- Activity level: ${personaAnswers.activity}
- Crowd preference: ${personaAnswers.crowds} crowds
- Accommodation: ${personaAnswers.accommodation}
- Remote destinations: ${personaAnswers.remote ? 'Yes' : 'No'}
- Timing flexibility: ${personaAnswers.timing}

Write in second person (e.g., "You are..."). Be specific and insightful. Keep it under 100 words.`;
  }
}
