import { motion } from 'framer-motion';

export default function DynamicBackground({ children }) {
    return (
        <div className="relative min-h-screen w-full overflow-hidden bg-background">
            {/* Calming Animated Background */}
            <div className="fixed inset-0 z-0 pointer-events-none">
                {/* Deep Base Gradient */}
                <div className="absolute inset-0 bg-gradient-to-br from-background via-surface to-background" />

                {/* Grid Overlay for Texture */}
                <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />

                {/* 1. Primary Organic Cell (Top Right) */}
                <motion.div
                    animate={{
                        y: [0, -20, 0],
                        scale: [1, 1.05, 1],
                        rotate: [0, 5, -5, 0],
                    }}
                    transition={{
                        duration: 18,
                        repeat: Infinity,
                        ease: "easeInOut"
                    }}
                    className="absolute -top-[10%] -right-[5%] w-[45%] h-[45%] bg-primary/10 blur-[100px] rounded-full mix-blend-screen"
                />

                {/* 2. Secondary Organic Cell (Bottom Left) */}
                <motion.div
                    animate={{
                        y: [0, 30, 0],
                        scale: [1, 1.1, 1],
                        rotate: [0, -5, 5, 0],
                    }}
                    transition={{
                        duration: 25,
                        repeat: Infinity,
                        ease: "easeInOut"
                    }}
                    className="absolute -bottom-[15%] -left-[5%] w-[40%] h-[40%] bg-secondary/15 blur-[120px] rounded-full mix-blend-screen"
                />

                {/* 3. Floating Particles (Pulse) */}
                <motion.div
                    animate={{
                        opacity: [0.1, 0.3, 0.1],
                        scale: [1, 1.2, 1],
                    }}
                    transition={{
                        duration: 8,
                        repeat: Infinity,
                        ease: "easeInOut"
                    }}
                    className="absolute top-1/4 left-1/3 w-32 h-32 bg-primary/5 blur-[50px] rounded-full"
                />
            </div>

            {/* Content Container */}
            <div className="relative z-10 w-full min-h-screen">
                {children}
            </div>
        </div>
    );
}
