import { Column, Entity, PrimaryColumn } from 'typeorm';

export interface QuestionOption {
    label: string;
    value: string;
}

@Entity({ name: 'questions' })
export class Question {
    @PrimaryColumn()
    id: string;

    @Column()
    key: string;

    @Column({ type: 'text' })
    question: string;

    @Column({ default: 'options' })
    type: string;

    @Column({ type: 'jsonb' })
    options: QuestionOption[];

    @Column({ type: 'int' })
    orderIndex: number;
}
