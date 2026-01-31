import { Controller, Get } from '@nestjs/common';
import { QuestionsService } from './questions.service';
import { Question } from './entities/question.entity';

@Controller('questions')
export class QuestionsController {
    constructor(private readonly questionsService: QuestionsService) { }

    @Get()
    async findAll(): Promise<Question[]> {
        return this.questionsService.findAll();
    }
}
