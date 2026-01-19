import { MigrationInterface, QueryRunner } from 'typeorm';
import * as path from 'path';
import * as fs from 'fs/promises';

interface QuestionSeed {
  id: string;
  key: string;
  question: string;
  type: string;
  options: { label: string; value: string }[];
}

export class SeedQuestions1737324000000 implements MigrationInterface {
  public async up(queryRunner: QueryRunner): Promise<void> {
    // Read questions from JSON file
    const filePath = path.join(__dirname, '..', '..', 'data', 'questions.json');
    const raw = await fs.readFile(filePath, 'utf8');
    const questions = JSON.parse(raw) as QuestionSeed[];

    // Upsert each question with proper order index
    // This allows the migration to be run multiple times safely
    for (let i = 0; i < questions.length; i++) {
      const q = questions[i];
      await queryRunner.query(
        `INSERT INTO questions (id, key, question, type, options, "orderIndex") 
         VALUES ($1, $2, $3, $4, $5, $6)
         ON CONFLICT (id) 
         DO UPDATE SET 
           key = EXCLUDED.key,
           question = EXCLUDED.question,
           type = EXCLUDED.type,
           options = EXCLUDED.options,
           "orderIndex" = EXCLUDED."orderIndex"`,
        [q.id, q.key, q.question, q.type, JSON.stringify(q.options), i],
      );
    }
  }

  public async down(queryRunner: QueryRunner): Promise<void> {
    // Remove all seeded questions
    await queryRunner.query(`DELETE FROM questions`);
  }
}
