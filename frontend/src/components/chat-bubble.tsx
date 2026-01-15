interface ChatBubbleProps {
  message: string;
  isBot: boolean;
  isDarkMode?: boolean;
}

export function ChatBubble({
  message,
  isBot,
  isDarkMode = false,
}: ChatBubbleProps) {
  return (
    <div
      className={`flex ${
        isBot ? "justify-start" : "justify-end"
      } mb-4 animate-fadeIn`}
    >
      <div
        className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${
          isBot
            ? isDarkMode
              ? "bg-gray-700 text-white"
              : "bg-primary/10 text-foreground border border-primary/20"
            : isDarkMode
            ? "bg-primary text-white"
            : "bg-primary text-white"
        }`}
      >
        <p className="text-sm leading-relaxed">{message}</p>
      </div>
    </div>
  );
}
