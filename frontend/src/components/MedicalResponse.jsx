import React from 'react';
import { Activity, AlertTriangle, CheckCircle, AlertOctagon, FileText, HeartPulse } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { motion } from 'framer-motion';

const MedicalResponse = ({ content }) => {
    // IMPROVED REGEX: Handles both **Bold**: and Plain: formats from LLM
    // LLM sometimes omits the ** markdown bold markers, so we match both patterns
    const sections = {
        // Match: "**Possible Causes**:" OR "Possible Causes:" (with/without bold)
        causes: /(?:\*\*)?Possible Causes(?:\*\*)?:\s*\n?([\s\S]*?)(?=\n(?:\*\*)?(?:Severity|Next|Red|$))/i,
        // Match: "**Severity Level**:" OR "Severity Level:" - capture value after colon
        severity: /(?:\*\*)?Severity(?: Level)?(?:\*\*)?:\s*([^\n]*)/i,
        // Match: "**Next Steps**:" OR next steps as numbered list (Step 1:, Step 2:, etc.)
        nextSteps: /(?:(?:\*\*)?Next Steps(?:\*\*)?:\s*\n?|(?=- Step 1:))([\s\S]*?)(?=\n(?:\*\*)?Red|$)/i,
        // Match: "**Red Flags**" with any suffix like "(Seek Emergency Care If):"
        redFlags: /(?:\*\*)?Red Flags(?:\*\*)?[^:\n]*:\s*\n?([\s\S]*?)$/i,
    };

    const causes = content.match(sections.causes)?.[1]?.trim();
    const severityMatch = content.match(sections.severity)?.[1]?.trim();
    // For Next Steps, also check for inline numbered steps format
    let nextSteps = content.match(sections.nextSteps)?.[1]?.trim();
    // Fallback: extract lines starting with "- Step" if header match failed
    if (!nextSteps) {
        const stepLines = content.match(/- Step \d+:[^\n]*/g);
        if (stepLines) nextSteps = stepLines.join('\n');
    }
    const redFlags = content.match(sections.redFlags)?.[1]?.trim();

    // -------------------------------------------------------------------------
    // 2. MARKDOWN CONFIGURATION
    // -------------------------------------------------------------------------
    const MarkdownComponents = {
        a: ({ node, ...props }) => (
            <a
                {...props}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:text-primary-hover underline font-semibold cursor-pointer transition-colors"
                onClick={(e) => e.stopPropagation()}
            >
                {props.children}
            </a>
        ),
        ul: ({ node, ...props }) => <ul {...props} className="list-disc pl-5 my-2 space-y-1 text-slate-300" />,
        ol: ({ node, ...props }) => <ol {...props} className="list-decimal pl-5 my-2 space-y-1 text-slate-300" />,
        li: ({ node, ...props }) => <li {...props} className="leading-relaxed text-slate-300" />,
        p: ({ node, ...props }) => <p {...props} className="mb-2 last:mb-0 leading-relaxed text-slate-300" />,
        strong: ({ node, ...props }) => <span {...props} className="font-bold text-primary" />
    };

    // Helper to render content safely with GFM support
    const renderMarkdown = (text, className = "") => (
        <div className={`markdown-content ${className}`}>
            <ReactMarkdown remarkPlugins={[remarkGfm]} components={MarkdownComponents}>
                {text}
            </ReactMarkdown>
        </div>
    );

    // -------------------------------------------------------------------------
    // 3. FALLBACK RENDERER
    // -------------------------------------------------------------------------
    if (!causes && !severityMatch && !nextSteps && !redFlags) {
        return (
            <div className="text-slate-300">
                {renderMarkdown(content)}
            </div>
        );
    }

    const getSeverityStyle = (level) => {
        const l = level?.toLowerCase() || "";
        if (l.includes("high")) return "bg-red-500/10 text-red-400 border-red-500/30";
        if (l.includes("medium")) return "bg-yellow-500/10 text-yellow-400 border-yellow-500/30";
        return "bg-teal-500/10 text-teal-400 border-teal-500/30";
    };

    const containerVariants = {
        hidden: { opacity: 0, y: 10 },
        visible: {
            opacity: 1,
            y: 0,
            transition: {
                when: "beforeChildren",
                staggerChildren: 0.1
            }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, x: -10 },
        visible: { opacity: 1, x: 0 }
    };

    return (
        <motion.div
            initial="hidden"
            animate="visible"
            variants={containerVariants}
            className="space-y-4 w-full font-sans text-sm"
        >
            {/* SEVERITY BADGE */}
            {severityMatch && (
                <motion.div variants={itemVariants} className={`flex items-center gap-2 p-3 rounded-lg border backdrop-blur-sm ${getSeverityStyle(severityMatch)}`}>
                    <Activity className="w-5 h-5 flex-shrink-0 animate-pulse-slow" />
                    <span className="font-bold uppercase tracking-wide">Severity: {severityMatch}</span>
                </motion.div>
            )}

            {/* 2. RED FLAGS (Highest Priority) */}
            {redFlags && (
                <motion.div variants={itemVariants} className="bg-red-950/20 border-l-4 border-red-500 p-4 rounded-r-lg">
                    <div className="flex items-center gap-2 text-red-400 font-bold mb-2">
                        <AlertOctagon className="w-5 h-5 flex-shrink-0" />
                        <h3 className="uppercase tracking-wide">Red Flags - Seek Care If:</h3>
                    </div>
                    {renderMarkdown(redFlags, "text-slate-300")}
                </motion.div>
            )}

            {/* 3. POSSIBLE CAUSES */}
            {causes && (
                <motion.div variants={itemVariants} className="bg-surface/50 border border-slate-700/50 p-4 rounded-lg">
                    <div className="flex items-center gap-2 text-primary font-bold mb-2">
                        <FileText className="w-5 h-5 flex-shrink-0" />
                        <h3 className="uppercase tracking-wide">Possible Causes</h3>
                    </div>
                    {renderMarkdown(causes, "text-slate-300")}
                </motion.div>
            )}

            {/* 4. NEXT STEPS */}
            {nextSteps && (
                <motion.div variants={itemVariants} className="bg-secondary/10 border border-secondary/30 p-4 rounded-lg">
                    <div className="flex items-center gap-2 text-secondary font-bold mb-2">
                        <CheckCircle className="w-5 h-5 flex-shrink-0" />
                        <h3 className="uppercase tracking-wide">Recommended Actions</h3>
                    </div>
                    {renderMarkdown(nextSteps, "text-slate-300")}
                </motion.div>
            )}

            {/* RESIDUAL CONTENT (Safety Net) */}
            {!content.includes("**") && !severityMatch && (
                <div className="pt-2 border-t border-slate-700/50 text-slate-500 text-xs italic flex items-center gap-1">
                    <HeartPulse className="w-3 h-3" />
                    Medical verification active.
                </div>
            )}
        </motion.div>
    );
};

export default MedicalResponse;