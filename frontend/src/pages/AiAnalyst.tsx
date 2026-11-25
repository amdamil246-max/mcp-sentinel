import React, { useState } from 'react';
import { api } from '../services/api';
import {
  Sparkles,
  Send,
  ShieldCheck,
  Bot,
  User,
  HelpCircle
} from 'lucide-react';

export const AiAnalyst: React.FC = () => {
  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'analyst'; text: string; details?: any }>>([
    {
      sender: 'analyst',
      text: "Hello! I am your AI Security Analyst. I can explain why tool calls were blocked, summarize security alerts, interpret complex commands, and recommend hardening remediations.",
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAsk = async (queryText?: string) => {
    const q = queryText || inputQuery;
    if (!q.trim()) return;

    const userMsg = { sender: 'user' as const, text: q };
    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setLoading(true);

    try {
      const res = await api.askAnalyst(q);
      const analystMsg = {
        sender: 'analyst' as const,
        text: res.response,
        details: res
      };
      setMessages((prev) => [...prev, analystMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'analyst' as const,
          text: `Analysis error: ${err.message}`
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const sampleQuestions = [
    "Why was the destructive command blocked?",
    "Explain prompt injection defense in MCP tool responses",
    "What remediation steps should be applied to high-risk tools?",
    "How does cryptographic audit chaining protect forensic evidence?"
  ];

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-wide flex items-center space-x-2">
          <Sparkles className="w-5 h-5 text-violet-400" />
          <span>AI Security Analyst Assistant</span>
        </h1>
        <p className="text-xs text-slate-400">
          Advisory security intelligence. Zero-trust compliant: redacts sensitive data and never overrides deterministic security policies.
        </p>
      </div>

      {/* Suggested Quick Prompts */}
      <div className="flex flex-wrap gap-2">
        {sampleQuestions.map((sq, idx) => (
          <button
            key={idx}
            onClick={() => handleAsk(sq)}
            className="px-3 py-1.5 rounded-lg sentinel-surface-interactive text-slate-200 text-xs flex items-center space-x-1.5"
          >
            <HelpCircle className="w-3 h-3 text-violet-400" />
            <span>{sq}</span>
          </button>
        ))}
      </div>

      {/* Chat Messages Container */}
      <div className="p-4 rounded-xl sentinel-surface min-h-[420px] max-h-[550px] overflow-y-auto space-y-4">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex items-start space-x-3 ${
              m.sender === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {m.sender === 'analyst' && (
              <div className="w-8 h-8 rounded-lg bg-violet-500/15 border border-violet-400/30 flex items-center justify-center text-violet-300 flex-shrink-0 mt-0.5">
                <Bot className="w-4 h-4" />
              </div>
            )}

            <div
              className={`p-3.5 rounded-xl max-w-2xl text-xs leading-relaxed ${
                m.sender === 'user'
                  ? 'bg-cyan-500/15 text-cyan-100 border border-cyan-400/30'
                  : 'sentinel-subsurface text-slate-200'
              }`}
            >
              {m.text}

              {m.details?.advisory && (
                <div className="mt-2 pt-2 border-t border-white/[0.08] text-[10px] text-slate-400 font-mono flex items-center space-x-1">
                  <ShieldCheck className="w-3 h-3 text-emerald-400" />
                  <span>Verified by Deterministic Firewall Baseline</span>
                </div>
              )}
            </div>

            {m.sender === 'user' && (
              <div className="w-8 h-8 rounded-lg sentinel-subsurface flex items-center justify-center text-slate-300 flex-shrink-0 mt-0.5">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center space-x-2 text-slate-400 text-xs pl-11">
            <Sparkles className="w-4 h-4 animate-spin text-violet-400" />
            <span>AI Analyst analyzing security context...</span>
          </div>
        )}
      </div>

      {/* Query Input */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleAsk();
        }}
        className="flex items-center space-x-2"
      >
        <input
          type="text"
          placeholder="Ask AI Analyst about threats, blocked commands, or remediation..."
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          className="flex-1 px-4 py-2.5 sentinel-surface rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-violet-400/50"
        />
        <button
          type="submit"
          disabled={loading || !inputQuery.trim()}
          className="px-4 py-2.5 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 shadow-lg shadow-violet-950/40 disabled:opacity-50 transition-all"
        >
          <Send className="w-3.5 h-3.5" />
          <span>Ask</span>
        </button>
      </form>
    </div>
  );
};
