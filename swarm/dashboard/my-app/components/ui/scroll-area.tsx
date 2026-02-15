import * as React from "react"
import { cn } from "@/lib/utils"

interface ScrollAreaProps extends React.ComponentProps<"div"> {
  orientation?: "vertical" | "horizontal" | "both"
}

function ScrollArea({
  className,
  children,
  orientation = "vertical",
  ...props
}: ScrollAreaProps) {
  const scrollClasses = {
    vertical: "overflow-y-auto overflow-x-hidden",
    horizontal: "overflow-x-auto overflow-y-hidden",
    both: "overflow-auto",
  }

  return (
    <div
      data-slot="scroll-area"
      className={cn(
        "relative h-full w-full",
        scrollClasses[orientation],
        "scrollbar-thin scrollbar-thumb-muted scrollbar-track-transparent",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export { ScrollArea }
