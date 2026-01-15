import { ChatOnboarding } from "@/components/chat-onboarding";

export default function OnboardingPage() {
  return (
    <div className="min-h-[calc(100vh-5rem)] flex flex-col bg-linear-to-br from-background via-primary/2 to-background">
      <main className="flex-1 flex flex-col">
        <div className="max-w-4xl mx-auto w-full flex-1 flex flex-col">
          {/* Header */}
          <div className="px-4 md:px-6 py-8 md:py-10 text-center border-b border-border/30">
            <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-2">
              {"Let's Plan Your Trip"}
            </h1>
            <p className="text-muted-foreground">
              Chat with Lotus to discover your perfect Vietnam experience in
              just 5 minutes
            </p>
          </div>

          {/* Chat area */}
          <ChatOnboarding />
        </div>
      </main>
    </div>
  );
}
