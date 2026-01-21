"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ChatBubble } from "@/components/chat-bubble";
import { Loader2, ArrowRight } from "lucide-react";
import { userService } from "@/services/user.service";
import { questionService, Question } from "@/services/question.service";

interface ChatMessage {
  id: string;
  text: string;
  isBot: boolean;
  timestamp: Date;
}

export function ChatOnboarding() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [conversationSteps, setConversationSteps] = useState<Question[]>([]);
  const [loadingQuestions, setLoadingQuestions] = useState(true);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const questions = await questionService.getQuestions();
        const sortedQuestions = questions.sort(
          (a, b) => a.orderIndex - b.orderIndex,
        );
        setConversationSteps(sortedQuestions);
        if (sortedQuestions.length > 0) {
          setMessages([
            {
              id: "1",
              text: sortedQuestions[0].question,
              isBot: true,
              timestamp: new Date(),
            },
          ]);
        }
      } catch (error) {
        console.error("Failed to fetch questions:", error);
      } finally {
        setLoadingQuestions(false);
      }
    };
    fetchQuestions();
  }, []);

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

  const handleContinue = async () => {
    const formattedAnswers = {
      duration: answers.duration || "",
      companions: answers.companions || "",
      budget: answers.budget || "",
      pace: answers.pace || "",
      travelStyle: answers.travelStyle || "",
      activity: answers.activity || "",
      crowds: answers.crowds || "",
      accommodation: answers.accommodation || "",
      remote: answers.remote === "yes",
      timing: answers.timing || "",
    };

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const response = await userService.submitOnboarding(formattedAnswers);
      localStorage.setItem("personaAnswers", JSON.stringify(formattedAnswers));
      if (response.userId) {
        localStorage.setItem("userId", response.userId);
      }
      router.push("/persona");
    } catch (error) {
      console.error("Failed to submit onboarding:", error);
      setSubmitError("Failed to save your preferences. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loadingQuestions || conversationSteps.length === 0) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Loading your questions...</p>
        </div>
      </div>
    );
  }

  const isCompleted =
    currentStep === conversationSteps.length - 1 &&
    !!answers[conversationSteps[currentStep]?.key];
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
              {submitError && (
                <div className="bg-destructive/10 border border-destructive/20 rounded-xl p-4 text-center">
                  <p className="text-sm text-destructive">{submitError}</p>
                </div>
              )}
              <Button
                onClick={handleContinue}
                disabled={isSubmitting}
                size="lg"
                className="w-full gap-2 h-12 font-semibold"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Saving Your Preferences...
                  </>
                ) : (
                  <>
                    See Your Travel Persona
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
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
