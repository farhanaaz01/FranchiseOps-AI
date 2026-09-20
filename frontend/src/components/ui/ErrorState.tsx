import React from 'react';
import { AlertTriangle, RefreshCw, WifiOff } from 'lucide-react';
import { cn } from '@/utils/cn';
import { Button } from './Button';

interface ErrorStateProps {
  title?: string;
  message?: string;
  /** Show network-specific error messaging */
  isNetworkError?: boolean;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Something went wrong',
  message = 'Failed to load data. Please try again.',
  isNetworkError = false,
  onRetry,
  className,
}) => (
  <div
    className={cn(
      'flex flex-col items-center justify-center gap-4 py-12 px-6 text-center',
      className
    )}
  >
    <div className="w-12 h-12 rounded-full bg-[rgba(208,85,90,0.12)] flex items-center justify-center">
      {isNetworkError ? (
        <WifiOff className="w-5 h-5 text-[#D0555A]" />
      ) : (
        <AlertTriangle className="w-5 h-5 text-[#D0555A]" />
      )}
    </div>
    <div>
      <p className="text-sm font-semibold text-[#EDEFF3] mb-1">{title}</p>
      <p className="text-xs text-[#5C6478] max-w-sm">{message}</p>
    </div>
    {onRetry && (
      <Button
        variant="outline"
        size="sm"
        leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
        onClick={onRetry}
      >
        Try again
      </Button>
    )}
  </div>
);

// ---- Inline Error Banner ----
interface ErrorBannerProps {
  message: string;
  onDismiss?: () => void;
  className?: string;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({
  message,
  onDismiss,
  className,
}) => (
  <div
    className={cn(
      'flex items-start gap-3 rounded-lg border border-[rgba(208,85,90,0.25)] bg-[rgba(208,85,90,0.08)] px-4 py-3',
      className
    )}
  >
    <AlertTriangle className="w-4 h-4 text-[#D0555A] shrink-0 mt-0.5" />
    <p className="flex-1 text-xs text-[#D0555A]">{message}</p>
    {onDismiss && (
      <button
        onClick={onDismiss}
        className="text-[#D0555A]/60 hover:text-[#D0555A] transition-colors ml-2"
        aria-label="Dismiss error"
      >
        ×
      </button>
    )}
  </div>
);
