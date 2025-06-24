import React from "react";
import { cn } from "#/utils/utils";

interface ButtonProps
  extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, "type"> {
  variant?: "default" | "outline" | "ghost";
  size?: "default" | "sm" | "lg";
  className?: string;
  type?: "button" | "submit" | "reset";
}

export function Button({
  className,
  variant = "default",
  size = "default",
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <button
      // eslint-disable-next-line react/button-has-type
      type={type}
      className={cn(
        "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background",
        {
          "bg-primary text-white hover:bg-primary/90": variant === "default",
          "border border-tertiary-light bg-white hover:bg-gray-50":
            variant === "outline",
          "hover:bg-gray-100": variant === "ghost",
        },
        {
          "h-10 py-2 px-4": size === "default",
          "h-9 px-3": size === "sm",
          "h-11 px-8": size === "lg",
        },
        className,
      )}
      // eslint-disable-next-line react/jsx-props-no-spreading
      {...props}
    />
  );
}
