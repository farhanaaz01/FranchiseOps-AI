import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertOctagon, RotateCcw, Home } from 'lucide-react';
import { Button } from './Button';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error safely without breaking user interface
    console.error('FranchiseOps AI ErrorBoundary caught:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: undefined });
  };

  private handleGoHome = () => {
    window.location.href = '/';
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#0E1015] flex items-center justify-center p-6 select-none">
          <div className="max-w-md w-full bg-[#12141A] border border-[#262B35] rounded-xl p-6 shadow-2xl space-y-5 text-center">
            <div className="w-12 h-12 rounded-xl bg-[#D0555A]/10 border border-[#D0555A]/30 flex items-center justify-center text-[#D0555A] mx-auto">
              <AlertOctagon className="w-6 h-6" />
            </div>

            <div className="space-y-1.5">
              <h2 className="text-base font-bold text-[#EDEFF3] font-display">
                Something went wrong
              </h2>
              <p className="text-xs text-[#8A93A6] leading-relaxed">
                An unexpected rendering error occurred in the operational dashboard. Session telemetry remains secure.
              </p>
            </div>

            <div className="p-3 bg-[#171A20] rounded-lg border border-[#262B35] text-[11px] font-mono text-[#5C6478] truncate">
              {this.state.error?.message || 'Uncaught Client Exception'}
            </div>

            <div className="flex items-center justify-center gap-3 pt-2">
              <Button
                variant="outline"
                size="sm"
                icon={<RotateCcw className="w-3.5 h-3.5" />}
                onClick={this.handleReset}
              >
                Try Again
              </Button>
              <Button
                variant="primary"
                size="sm"
                icon={<Home className="w-3.5 h-3.5" />}
                onClick={this.handleGoHome}
              >
                Return to Dashboard
              </Button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
