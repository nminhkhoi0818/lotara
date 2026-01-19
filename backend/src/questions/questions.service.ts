import { Injectable, Logger, OnModuleInit } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Question } from './entities/question.entity';
import * as fs from 'fs/promises';
import * as path from 'path';

interface QuestionSeed {
    id: string;
    key: string;
    question: string;
    type: string;
    options: { label: string; value: string }[];
}

@Injectable()
export class QuestionsService implements OnModuleInit {
    private readonly logger = new Logger(QuestionsService.name);

    constructor(
        @InjectRepository(Question)
        private readonly questionRepo: Repository<Question>,
    ) { }

    async onModuleInit(): Promise<void> {
        await this.seedIfEmpty();
    }

    async findAll(): Promise<Question[]> {
        return this.questionRepo.find({ order: { orderIndex: 'ASC' } });
    }

    private async seedIfEmpty(): Promise<void> {
        const existing = await this.questionRepo.count();
        if (existing > 0) return;

        try {
            const filePath = path.join(process.cwd(), 'data', 'questions.json');
            const raw = await fs.readFile(filePath, 'utf8');
            const parsed = JSON.parse(raw) as QuestionSeed[];
            const records = parsed.map((item, index) =>
                this.questionRepo.create({
                    id: item.id,
                    key: item.key,
                    question: item.question,
                    type: item.type,
                    options: item.options,
                    orderIndex: index,
                }),
            );
            await this.questionRepo.save(records);
            this.logger.log(`Seeded ${records.length} onboarding questions`);
        } catch (error) {
            const trace = error instanceof Error ? error.stack : String(error);
            this.logger.error('Failed to seed onboarding questions', trace);
        }
    }
}
