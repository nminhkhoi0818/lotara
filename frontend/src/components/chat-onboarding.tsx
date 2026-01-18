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
      "Hi there! I'm Lotus, your AI travel companion. I'm excited to help you plan your perfect Vietnam trip. Let's start with the most important question - how long will you be traveling in Vietnam?",
    key: "duration",
    type: "options",
    options: [
      { label: "3-5 days (quick trip)", value: "short" },
      { label: "1-2 weeks (standard trip)", value: "medium" },
      { label: "2-4 weeks (extended trip)", value: "long" },
      { label: "1 month+ (long-term travel)", value: "extended" },
    ],
  },
  {
    id: "companions",
    question: "Great! Now, who will be joining you on this adventure?",
    key: "companions",
    type: "options",
    options: [
      { label: "Just me (solo adventure)", value: "solo" },
      { label: "My partner (couple's trip)", value: "couple" },
      { label: "Family with young children", value: "family_kids" },
      { label: "Family (adults only)", value: "family_adults" },
      { label: "Friends group", value: "friends" },
    ],
  },
  {
    id: "budget",
    question:
      "Perfect! What's your daily budget per person? (including accommodation, food, and activities)",
    key: "budget",
    type: "options",
    options: [
      { label: "Budget ($20-50/day)", value: "budget" },
      { label: "Mid-range ($50-100/day)", value: "midrange" },
      { label: "Comfortable ($100-200/day)", value: "comfortable" },
      { label: "Luxury ($200+/day)", value: "luxury" },
    ],
  },
  {
    id: "pace",
    question: "Excellent! What's your preferred travel pace?",
    key: "pace",
    type: "options",
    options: [
      { label: "Slow & deep - stay longer in fewer places", value: "slow" },
      {
        label: "Balanced - mix of exploration and relaxation",
        value: "balanced",
      },
      { label: "Fast-paced - see as much as possible", value: "fast" },
    ],
  },
  {
    id: "travelStyle",
    question:
      "What's your TOP priority for this trip? (we'll personalize everything around this!)",
    key: "travelStyle",
    type: "options",
    options: [
      { label: "Adventure & outdoor activities", value: "adventure" },
      { label: "Culture & history immersion", value: "cultural" },
      { label: "Nature, beaches & scenic beauty", value: "nature" },
      { label: "Food & culinary experiences", value: "food" },
      { label: "Relaxation & wellness", value: "wellness" },
      { label: "Photography & Instagram-worthy spots", value: "photography" },
    ],
  },
  {
    id: "activity",
    question: "How physically active do you want to be during your trip?",
    key: "activity",
    type: "options",
    options: [
      {
        label: "Relaxed pace - minimal walking, mostly transport",
        value: "low",
      },
      {
        label: "Moderately active - comfortable walking & light activities",
        value: "medium",
      },
      {
        label: "Very active - hiking, biking, full-day adventures",
        value: "high",
      },
    ],
  },
  {
    id: "crowds",
    question: "How do you feel about tourist crowds and popular hotspots?",
    key: "crowds",
    type: "options",
    options: [
      {
        label: "Avoid crowds - prefer hidden gems & local spots",
        value: "avoid",
      },
      { label: "Mix of both - main sights + off-beaten-path", value: "mixed" },
      {
        label: "Embrace crowds - don't miss the iconic spots",
        value: "embrace",
      },
    ],
  },
  {
    id: "accommodation",
    question: "What type of accommodation suits you best?",
    key: "accommodation",
    type: "options",
    options: [
      {
        label: "Hostels & guesthouses - social & budget-friendly",
        value: "hostel",
      },
      {
        label: "Standard hotels - clean, comfortable & reliable",
        value: "standard",
      },
      {
        label: "Boutique hotels - unique character & charm",
        value: "boutique",
      },
      { label: "Luxury resorts & 5-star hotels", value: "premium" },
    ],
  },
  {
    id: "remote",
    question: "Will you need to work remotely, or is this a full vacation?",
    key: "remote",
    type: "options",
    options: [
      { label: "Yes, I need reliable WiFi for work", value: "yes" },
      { label: "No, I'm fully unplugging", value: "no" },
    ],
  },
  {
    id: "timing",
    question: "Last one! When do you prefer to explore and do activities?",
    key: "timing",
    type: "options",
    options: [
      {
        label: "Early mornings - sunrise adventures & beat the crowds",
        value: "morning",
      },
      { label: "Flexible - spread throughout the day", value: "flexible" },
      {
        label: "Late start - sleep in, afternoons & evenings",
        value: "evening",
      },
    ],
  },
];

const initialAnswers = {
  duration: "",
  companions: "",
  budget: "",
  pace: "",
  travelStyle: "",
  activity: "",
  crowds: "",
  accommodation: "",
  remote: "",
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
      duration: answers.duration,
      companions: answers.companions,
      budget: answers.budget,
      pace: answers.pace,
      travelStyle: answers.travelStyle,
      activity: answers.activity,
      crowds: answers.crowds,
      accommodation: answers.accommodation,
      remote: answers.remote === "yes",
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
