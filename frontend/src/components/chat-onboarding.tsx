"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ChatBubble } from "@/components/chat-bubble";
import { Loader2, ArrowRight } from "lucide-react";

interface ConversationStep {
  id: string;
  question: string;
  key: keyof typeof initialAnswers;
  options?: { label: string; value: string }[];
  type: "free-text" | "options";
}

const conversationSteps: ConversationStep[] = [
  {
    id: "intro",
    question:
      "Hi there! I'm Lotus, your AI travel companion. I'm excited to help you plan your perfect Vietnam trip. Let's start by understanding your travel style. What's your budget for this trip?",
    key: "budget",
    type: "options",
    options: [
      { label: "Budget conscious ($20-50/day)", value: "budget" },
      { label: "Moderate ($50-100/day)", value: "moderate" },
      { label: "Comfortable ($100-200/day)", value: "comfortable" },
      { label: "Luxury ($200+/day)", value: "luxury" },
    ],
  },
  {
    id: "remote",
    question:
      "Great choice! Now, will you be working remotely during your trip, or is this a full vacation?",
    key: "remote",
    type: "options",
    options: [
      { label: "Yes, I need a workcation", value: "yes" },
      { label: "No, I'm on full vacation", value: "no" },
    ],
  },
  {
    id: "crowds",
    question: "Perfect! How do you feel about crowds and busy atmospheres?",
    key: "crowds",
    type: "options",
    options: [
      { label: "I prefer quiet, solitude", value: "avoid" },
      { label: "Doesn't matter to me", value: "neutral" },
      { label: "I love vibrant, busy places", value: "enjoy" },
    ],
  },
  {
    id: "travelStyle",
    question:
      "Awesome! What's your ideal travel style? What activities excite you the most?",
    key: "travelStyle",
    type: "options",
    options: [
      { label: "Adventure & outdoor activities", value: "adventure" },
      { label: "Culture & history immersion", value: "cultural" },
      { label: "Relaxation & wellness", value: "relaxation" },
      { label: "Food & culinary experiences", value: "food" },
    ],
  },
  {
    id: "timing",
    question:
      "Last question! Are you a morning person or a night owl? How do you prefer to spend your time?",
    key: "timing",
    type: "options",
    options: [
      { label: "Early bird - up at dawn", value: "early" },
      { label: "Balanced - both early and late", value: "balanced" },
      { label: "Night owl - prefer evenings", value: "night" },
    ],
  },
];

const initialAnswers = {
  budget: "",
  remote: "",
  crowds: "",
  travelStyle: "",
  timing: "",
};

interface ChatMessage {
  id: string;
  text: string;
  isBot: boolean;
  timestamp: Date;
}

export function ChatOnboarding() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      text: conversationSteps[0].question,
      isBot: true,
      timestamp: new Date(),
    },
  ]);
  const [answers, setAnswers] = useState(initialAnswers);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleOptionSelect = async (value: string) => {
    const currentQuestion = conversationSteps[currentStep];

    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      text:
        currentQuestion.options?.find((opt) => opt.value === value)?.label ||
        value,
      isBot: false,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setAnswers({
      ...answers,
      [currentQuestion.key]: value,
    });

    setIsLoading(true);

    setTimeout(() => {
      if (currentStep < conversationSteps.length - 1) {
        const nextStep = currentStep + 1;
        setCurrentStep(nextStep);
        const nextQuestion = conversationSteps[nextStep];
        const botMessage: ChatMessage = {
          id: `msg-${Date.now()}`,
          text: nextQuestion.question,
          isBot: true,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, botMessage]);
      } else {
        const completionMessage: ChatMessage = {
          id: `msg-${Date.now()}`,
          text: "Perfect! I've learned everything I need to create your personalized trip. Let's see your travel persona!",
          isBot: true,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, completionMessage]);
      }
      setIsLoading(false);
    }, 600);
  };

  const handleContinue = () => {
    const formattedAnswers = {
      budget: answers.budget,
      remote: answers.remote === "yes",
      crowds: answers.crowds === "enjoy",
      travelStyle: answers.travelStyle,
      timing: answers.timing,
    };
    localStorage.setItem("personaAnswers", JSON.stringify(formattedAnswers));
    router.push("/persona");
  };

  const isCompleted =
    currentStep === conversationSteps.length - 1 && answers.timing !== "";
  const currentQuestion = conversationSteps[currentStep];

  return (
    <div className="h-full flex flex-col">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 md:py-8">
        <div className="max-w-2xl mx-auto space-y-4">
          {messages.map((message) => (
            <ChatBubble
              key={message.id}
              message={message.text}
              isBot={message.isBot}
            />
          ))}
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="bg-primary/10 text-foreground border border-primary/20 rounded-2xl px-4 py-3 flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-primary" />
                <span className="text-sm">Lotus is thinking...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input area */}
      <div className="border-t border-border/30 bg-linear-to-t from-background to-transparent p-4 md:p-6">
        <div className="max-w-2xl mx-auto">
          {isCompleted ? (
            <div className="space-y-4">
              <div className="bg-linear-to-r from-primary/10 to-secondary/10 border border-primary/20 rounded-2xl p-6 text-center">
                <h3 className="font-semibold text-foreground mb-2">
                  {"You're all set!"}
                </h3>
                <p className="text-sm text-muted-foreground mb-4">
                  {
                    "I've gathered all the information I need to create your perfect itinerary."
                  }
                </p>
              </div>
              <Button
                onClick={handleContinue}
                size="lg"
                className="w-full gap-2 h-12 font-semibold"
              >
                See Your Travel Persona
                <ArrowRight className="w-5 h-5" />
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {currentQuestion.type === "options" && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {currentQuestion.options?.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => handleOptionSelect(option.value)}
                      disabled={isLoading}
                      className="p-3 rounded-xl border-2 border-border hover:border-primary/30 hover:bg-accent/5 transition-all text-left text-sm font-medium text-foreground disabled:opacity-50"
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              )}

              {/* Progress indicator */}
              <div className="flex justify-between items-center mt-6 pt-4 border-t border-border/30">
                <span className="text-xs font-medium text-muted-foreground">
                  Step {currentStep + 1} of {conversationSteps.length}
                </span>
                <div className="flex gap-1">
                  {conversationSteps.map((_, idx) => (
                    <div
                      key={idx}
                      className={`h-1 rounded-full transition-all ${
                        idx <= currentStep ? "bg-primary w-4" : "bg-border w-2"
                      }`}
                    />
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
