"use client"

import React, { createContext, useContext, useState } from "react";
import { cn } from "@/lib/utils";

interface ToastProps {
  message: string;
  type?: "success" | "error" | "info";
  duration?: number;
}

interface ToastContextType {
  toast: (props: ToastProps) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<(ToastProps & { id: number })[]>([]);
  const [counter, setCounter] = useState(0);

  const toast = ({ message, type = "info", duration = 3000 }: ToastProps) => {
    const id = counter;
    setCounter((prev) => prev + 1);
    
    setToasts((prev) => [...prev, { message, type, duration, id }]);
    
    setTimeout(() => {
      setToasts((prev) => prev.filter((toast) => toast.id !== id));
    }, duration);
  };

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={cn(
              "rounded-md p-4 shadow-md",
              toast.type === "success" && "bg-green-500 text-white",
              toast.type === "error" && "bg-red-500 text-white",
              toast.type === "info" && "bg-blue-500 text-white"
            )}
          >
            {toast.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}

// Simple mock for the sonner toast function
export const toast = {
  success: (message: string) => {
    console.log(`Success: ${message}`);
  },
  error: (message: string) => {
    console.log(`Error: ${message}`);
  },
  info: (message: string) => {
    console.log(`Info: ${message}`);
  },
};
