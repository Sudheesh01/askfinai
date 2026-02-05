import * as React from "react";

import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(({ className, ...props }, ref) => (
  <input
    ref={ref}
    className={cn(
      "flex h-10 w-full rounded-md border border-fin-border bg-fin-surface px-3 py-2 text-sm text-fin-text placeholder:text-fin-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fin-accent",
      className
    )}
    {...props}
  />
));
Input.displayName = "Input";

export { Input };
