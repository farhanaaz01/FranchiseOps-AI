import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Sparkles, Send, Bot, User, CornerDownLeft, AlertCircle, ArrowRight } from 'lucide-react';

const SUGGESTED_QUESTIONS = [
  { text: 'Why is this outlet underperforming?', path: '/decision-center' },
  { text: 'Which outlets require attention?', path: '/decision-center' },
  { text: 'What are the current inventory risks?', path: '/inventory' },
  { text: 'What workforce issues are detected?', path: '/workforce' },
  { text: 'Which campaigns need attention?', path: '/marketing' },
  { text: 'What are the latest recommendations?', path: '/decision-center' },
];

export const OperationalCopilotChat: React.FC = () => {
  const navigate = useNavigate();
  const [input, setInput] = useState('');
  const [attemptedQuery, setAttemptedQuery] = useState<string | null>(null);

  const handleQuerySubmit = (queryText: string) => {
    if (!queryText.trim()) return;
    setAttemptedQuery(queryText.trim());
    setInput('');
  };

  return (
    <Card className="flex flex-col h-[580px]">
      <CardHeader separator>
        <div className="flex items-center justify-between w-full">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-[#6C8CFF]/10 text-[#6C8CFF]">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <CardTitle>Autonomous Operations Copilot</CardTitle>
              <span className="text-xs text-[#5C6478]">
                Interactive operational reasoning grounded in pipeline telemetry
              </span>
            </div>
          </div>
          <span className="text-[10px] font-mono text-[#E8A33D] bg-[#E8A33D]/10 px-2 py-0.5 rounded border border-[#E8A33D]/30">
            Assistant Shell
          </span>
        </div>
      </CardHeader>

      <CardContent className="p-4 flex flex-col flex-1 justify-between gap-4 overflow-hidden">
        {/* Backend Connection Status Notice */}
        <div className="p-3.5 rounded-lg bg-[#E8A33D]/5 border border-[#E8A33D]/25 flex items-start gap-3">
          <AlertCircle className="w-4 h-4 text-[#E8A33D] shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <span className="text-xs font-semibold text-[#EDEFF3]">
              Copilot backend connection not available
            </span>
            <p className="text-[11px] text-[#8A93A6] leading-relaxed">
              A conversational LLM inference endpoint is not exposed by the FastAPI server. To inspect operational reasoning, browse the deterministic Root Cause Engine findings below or visit the Operational Decision Center.
            </p>
          </div>
        </div>

        {/* Message Area */}
        <div className="flex-1 overflow-y-auto space-y-3 p-1">
          {attemptedQuery ? (
            <div className="space-y-3">
              {/* User Prompt */}
              <div className="flex items-start gap-2 justify-end">
                <div className="p-3 bg-[#1D212A] border border-[#262B35] rounded-xl rounded-tr-xs text-xs text-[#EDEFF3] max-w-[85%]">
                  {attemptedQuery}
                </div>
                <div className="p-1.5 rounded-md bg-[#262B35] text-[#8A93A6] shrink-0 mt-1">
                  <User className="w-3.5 h-3.5" />
                </div>
              </div>

              {/* System Honest Response */}
              <div className="flex items-start gap-2">
                <div className="p-1.5 rounded-md bg-[#6C8CFF]/10 text-[#6C8CFF] shrink-0 mt-1">
                  <Bot className="w-3.5 h-3.5" />
                </div>
                <div className="p-3.5 bg-[#171A20] border border-[#262B35] rounded-xl rounded-tl-xs text-xs space-y-2 max-w-[85%]">
                  <span className="text-[10px] font-mono uppercase text-[#E8A33D] font-bold block">
                    Copilot backend connection not available
                  </span>
                  <p className="text-[#8A93A6] leading-relaxed">
                    Live natural-language synthesis is not connected. Telemetry relevant to <em>"{attemptedQuery}"</em> is available directly in the structured decision workflows:
                  </p>
                  <div className="flex items-center gap-2 pt-1 flex-wrap">
                    <Button
                      variant="primary"
                      size="sm"
                      className="text-xs"
                      onClick={() => navigate('/decision-center')}
                    >
                      Open Decision Center
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="text-xs"
                      onClick={() => setAttemptedQuery(null)}
                    >
                      Clear
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="py-6 text-center space-y-3">
              <Bot className="w-8 h-8 text-[#5C6478] mx-auto" />
              <div className="space-y-1">
                <p className="text-xs text-[#EDEFF3] font-medium">
                  Operational Assistant Ready
                </p>
                <p className="text-[11px] text-[#5C6478] max-w-sm mx-auto">
                  Select a suggested diagnostic question below to navigate to the corresponding telemetry and decision workflows.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Suggested Queries Pills */}
        <div className="space-y-1.5 pt-2 border-t border-[#262B35]">
          <span className="text-[10px] font-mono text-[#5C6478] uppercase tracking-wider block">
            Suggested Diagnostic Queries
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
            {SUGGESTED_QUESTIONS.map((q, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setInput(q.text);
                  handleQuerySubmit(q.text);
                }}
                className="text-left px-2.5 py-1.5 rounded-lg bg-[#171A20] hover:bg-[#1D212A] border border-[#262B35] text-[11px] text-[#8A93A6] hover:text-[#EDEFF3] transition-colors truncate flex items-center justify-between group"
              >
                <span className="truncate">{q.text}</span>
                <ArrowRight className="w-3 h-3 text-[#5C6478] group-hover:text-[#6C8CFF] shrink-0 ml-1" />
              </button>
            ))}
          </div>
        </div>

        {/* Input Bar */}
        <div className="relative pt-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleQuerySubmit(input);
            }}
            placeholder="Ask an operational question (e.g. Why is OUT-02 underperforming?)..."
            className="w-full pl-3 pr-10 py-2 bg-[#171A20] border border-[#262B35] rounded-lg text-xs text-[#EDEFF3] placeholder-[#5C6478] focus:outline-hidden focus:border-[#6C8CFF] transition-colors"
          />
          <button
            onClick={() => handleQuerySubmit(input)}
            disabled={!input.trim()}
            className="absolute right-2 top-3 p-1 rounded text-[#6C8CFF] disabled:text-[#5C6478] hover:bg-[#1D212A] transition-colors"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </CardContent>
    </Card>
  );
};
