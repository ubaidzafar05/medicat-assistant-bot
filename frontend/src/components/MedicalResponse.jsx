import React from 'react';
import { Activity, AlertTriangle, CheckCircle, AlertOctagon, FileText } from 'lucide-react';

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

    // If no structured headers are found yet (during streaming), just show the text
    if (!causes && !severityMatch && !nextSteps && !redFlags) {
        return <div className="whitespace-pre-wrap text-slate-800 leading-relaxed">{content}</div>;
    }

    const getSeverityStyle = (level) => {
        const l = level?.toLowerCase() || "";
        if (l.includes("high")) return "bg-red-100 text-red-800 border-red-200";
        if (l.includes("medium")) return "bg-yellow-100 text-yellow-800 border-yellow-200";
        return "bg-green-100 text-green-800 border-green-200";
    };

    return (
        <div className="space-y-4 w-full font-sans">

            {/* 1. SEVERITY BADGE */}
            {severityMatch && (
                <div className={`flex items-center gap-2 p-3 rounded-lg border ${getSeverityStyle(severityMatch)} animate-in fade-in duration-500`}>
                    <Activity className="w-5 h-5" />
                    <span className="font-bold uppercase tracking-wide text-sm">Severity: {severityMatch}</span>
                </div>
            )}

            {/* 2. RED FLAGS (Highest Priority) */}
            {redFlags && (
                <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-md shadow-sm">
                    <div className="flex items-center gap-2 text-red-700 font-bold mb-1">
                        <AlertOctagon className="w-5 h-5" />
                        <h3 className="text-sm">RED FLAGS - Seek Care If:</h3>
                    </div>
                    <div className="text-red-900 leading-relaxed whitespace-pre-line text-sm">
                        {redFlags}
                    </div>
                </div>
            )}

            {/* 3. POSSIBLE CAUSES */}
            {causes && (
                <div className="bg-slate-50 border border-slate-200 p-4 rounded-lg shadow-sm">
                    <div className="flex items-center gap-2 text-slate-700 font-bold mb-1">
                        <FileText className="w-5 h-5" />
                        <h3 className="text-sm uppercase tracking-tight">Possible Causes</h3>
                    </div>
                    <div className="text-slate-800 leading-relaxed whitespace-pre-line text-sm">
                        {causes}
                    </div>
                </div>
            )}

            {/* 4. NEXT STEPS */}
            {nextSteps && (
                <div className="bg-emerald-50 border border-emerald-100 p-4 rounded-lg shadow-sm">
                    <div className="flex items-center gap-2 text-emerald-700 font-bold mb-1">
                        <CheckCircle className="w-5 h-5" />
                        <h3 className="text-sm">Recommended Actions</h3>
                    </div>
                    <div className="text-emerald-900 leading-relaxed whitespace-pre-line text-sm">
                        {nextSteps}
                    </div>
                </div>
            )}

            {/* Fallback for anything not caught by regex */}
            {!content.includes("**") && <div className="text-slate-500 text-xs italic pt-2 border-t mt-4">Standard medical advisory active.</div>}
        </div>
    );
};

export default MedicalResponse;