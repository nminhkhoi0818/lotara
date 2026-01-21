import { get } from "@/lib/api-client";

export interface QuestionOption {
  label: string;
  value: string;
}

export interface Question {
  id: string;
  key: string;
  question: string;
  type: string;
  options: QuestionOption[];
  orderIndex: number;
}

export const questionService = {
  getQuestions: async (): Promise<Question[]> => {
    return get<Question[]>("/questions");
  },
};
