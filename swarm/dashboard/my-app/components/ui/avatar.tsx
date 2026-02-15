import * as React from "react"
import { cn } from "@/lib/utils"

interface AvatarProps extends React.ComponentProps<"div"> {
  src?: string
  alt?: string
  fallback?: string
}

function Avatar({ className, src, alt, fallback, ...props }: AvatarProps) {
  return (
    <div
      data-slot="avatar"
      className={cn(
        "relative flex size-8 shrink-0 overflow-hidden rounded-full",
        className
      )}
      {...props}
    >
      {src ? (
        <img
          src={src}
          alt={alt}
          className="aspect-square size-full object-cover"
        />
      ) : (
        <div className="flex h-full w-full items-center justify-center bg-muted text-xs font-medium">
          {fallback}
        </div>
      )}
    </div>
  )
}

export { Avatar }
