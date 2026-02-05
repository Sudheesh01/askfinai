import { Card } from "@/components/ui/card";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
}

export default function ChatMessage({ role, content }: ChatMessageProps) {
  return (
    <div className={role === "user" ? "flex justify-end" : "flex justify-start"}>
      <Card className={role === "user" ? "max-w-[80%] bg-fin-accent/20" : "max-w-[80%]"}>
        <p className="whitespace-pre-wrap text-sm text-fin-text">{content}</p>
      </Card>
    </div>
  );
}
