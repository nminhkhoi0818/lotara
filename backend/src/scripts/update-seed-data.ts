#!/usr/bin/env ts-node

import { AppDataSource } from '../data-source';
import * as path from 'path';
import * as fs from 'fs/promises';

interface QuestionSeed {
  id: string;
  key: string;
  question: string;
  type: string;
  options: { label: string; value: string }[];
}

async function updateSeedData() {
  console.log('🌱 Starting seed data update...');

  try {
    // Initialize database connection
    await AppDataSource.initialize();
    console.log('✓ Database connected');

    // Read questions from JSON file
    const filePath = path.join(__dirname, '..', '..', 'data', 'questions.json');
    const raw = await fs.readFile(filePath, 'utf8');
    const questions = JSON.parse(raw) as QuestionSeed[];
    console.log(`✓ Loaded ${questions.length} questions from file`);

    // Upsert each question
    for (let i = 0; i < questions.length; i++) {
      const q = questions[i];
      await AppDataSource.query(
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
    console.log(`✓ Successfully updated ${questions.length} questions`);

    // Check for orphaned questions (in DB but not in file)
    const result = await AppDataSource.query(
      `SELECT id FROM questions WHERE id NOT IN (${questions.map((_, i) => `$${i + 1}`).join(',')})`,
      questions.map((q) => q.id),
    );

    if (result.length > 0) {
      console.log(
        `⚠ Warning: ${result.length} questions exist in database but not in questions.json:`,
      );
      result.forEach((row: any) => console.log(`  - ${row.id}`));
      console.log(
        '  Consider removing these manually or adding them back to questions.json',
      );
    }

    await AppDataSource.destroy();
    console.log('✓ Database connection closed');
    console.log('🎉 Seed data update completed successfully!');
    process.exit(0);
  } catch (error) {
    console.error('❌ Error updating seed data:', error);
    if (AppDataSource.isInitialized) {
      await AppDataSource.destroy();
    }
    process.exit(1);
  }
}

updateSeedData();
