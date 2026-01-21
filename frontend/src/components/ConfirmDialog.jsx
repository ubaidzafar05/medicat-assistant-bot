import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertTriangle, X } from 'lucide-react';

const ConfirmDialog = ({ isOpen, title, message, onConfirm, onCancel, confirmText = "Confirm", cancelText = "Cancel", variant = "default" }) => {
    if (!isOpen) return null;

    const variants = {
        default: {
            confirmBtn: "bg-accent hover:bg-sky-400 text-slate-900",
            icon: null
        },
        warning: {
            confirmBtn: "bg-amber-500 hover:bg-amber-400 text-slate-900",
            icon: <AlertTriangle className="w-6 h-6 text-amber-500" />
        },
        danger: {
            confirmBtn: "bg-red-500 hover:bg-red-400 text-white",
            icon: <AlertTriangle className="w-6 h-6 text-red-500" />
        }
    };

    const style = variants[variant] || variants.default;

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onCancel}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
                    />

                    {/* Dialog */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50
                            w-full max-w-md bg-slate-800 rounded-xl shadow-2xl border border-slate-700 p-6"
                    >
                        {/* Close button */}
                        <button
                            onClick={onCancel}
                            className="absolute top-4 right-4 text-slate-500 hover:text-slate-300 transition-colors"
                        >
                            <X className="w-5 h-5" />
                        </button>

                        {/* Content */}
                        <div className="flex items-start gap-4">
                            {style.icon && (
                                <div className="flex-shrink-0 mt-0.5">
                                    {style.icon}
                                </div>
                            )}
                            <div className="flex-1">
                                <h3 className="text-lg font-semibold text-white mb-2">
                                    {title}
                                </h3>
                                <p className="text-slate-400 text-sm">
                                    {message}
                                </p>
                            </div>
                        </div>

                        {/* Actions */}
                        <div className="flex justify-end gap-3 mt-6">
                            <button
                                onClick={onCancel}
                                className="px-4 py-2 text-sm font-medium text-slate-400 
                                    hover:text-white transition-colors rounded-lg
                                    hover:bg-slate-700"
                            >
                                {cancelText}
                            </button>
                            <button
                                onClick={onConfirm}
                                className={`px-4 py-2 text-sm font-bold rounded-lg transition-colors ${style.confirmBtn}`}
                            >
                                {confirmText}
                            </button>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
};

export default ConfirmDialog;
