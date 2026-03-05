import React, { useState } from 'react';
import { useLogin, useNotify, Notification } from 'react-admin';
import { motion } from 'framer-motion';
import { Mail, Lock } from 'lucide-react';
import { NetworkGlobe } from './NetworkGlobe';

export const CustomLogin = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const login = useLogin();
    const notify = useNotify();

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        login({ username, password }).catch((error) => {
            setLoading(false);
            notify(
                typeof error === 'string'
                    ? error
                    : error?.message || 'ra.auth.sign_in_error',
                { type: 'error' }
            );
        });
    };

    // Staggered animation variants
    const containerVariants = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: { staggerChildren: 0.1, delayChildren: 0.3 }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 20 },
        show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 24 } }
    };

    return (
        <div dir="rtl" className="min-h-screen w-full bg-black grid grid-cols-1 lg:grid-cols-2 text-white overflow-hidden font-sans">
            {/* Right Half: Glassmorphic Form (RTL Start) */}
            <div className="relative flex flex-col justify-center items-center p-8 lg:p-24 z-10 w-full min-h-screen">
                {/* Tighter, more vibrant ambient glow that doesn't wash out the darkness */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[350px] h-[350px] bg-[#0066FF] opacity-20 blur-[130px] rounded-full pointer-events-none" />
                
                <motion.div 
                    initial="hidden"
                    animate="show"
                    variants={containerVariants}
                    className="w-full max-w-md backdrop-blur-3xl bg-[#ffffff05] border border-[#ffffff15] rounded-3xl p-10 shadow-[0_8px_32px_0_rgba(0,0,0,0.5)] relative overflow-hidden"
                >
                    {/* Top inner glow highlight */}
                    <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" />
                    <div className="absolute top-0 inset-x-0 h-24 bg-gradient-to-b from-white/[0.02] to-transparent pointer-events-none" />
                    
                    <motion.div variants={itemVariants} className="mb-10 text-right relative z-10">
                        <motion.a 
                            href="/"
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className="flex items-center gap-4 group mb-8 w-fit"
                        >
                            {/* App Icon (Right side in RTL) */}
                            <div className="relative flex items-center justify-center w-[52px] h-[52px] transition-all duration-500 rounded-2xl group-hover:shadow-[0_0_20px_rgba(0,102,255,0.4)] bg-transparent">
                                <img 
                                    src="/images/icon.svg" 
                                    alt="Wateen" 
                                    className="w-full h-full object-contain relative z-10 transition-all duration-500 group-hover:scale-105 opacity-90 group-hover:opacity-100 rounded-2xl" 
                                />
                            </div>

                            {/* Arabic Text (Left side in RTL) */}
                            <div className="flex flex-col relative justify-center">
                                <div className="relative flex items-center justify-center pb-1">
                                    {/* Default White Text */}
                                    <span className="text-[38px] font-black text-white/90 drop-shadow-sm leading-none transition-opacity duration-500 group-hover:opacity-0 relative z-10">
                                        وتين
                                    </span>
                                    {/* Hover Gradient Text */}
                                    <span className="text-[38px] font-black text-transparent bg-clip-text bg-gradient-to-l from-cyan-400 via-blue-500 to-purple-600 drop-shadow-[0_0_15px_rgba(0,102,255,0.4)] leading-none opacity-0 transition-opacity duration-500 group-hover:opacity-100 absolute inset-0 z-0 flex items-center">
                                        وتين
                                    </span>
                                </div>
                                {/* Underline Container */}
                                <div className="relative h-1 mt-0.5 w-full">
                                    {/* Default White Underline */}
                                    <div className="absolute inset-0 bg-white/30 rounded-full transition-opacity duration-500 group-hover:opacity-0" />
                                    {/* Hover Gradient Underline */}
                                    <div className="absolute right-0 top-0 bottom-0 w-[100%] bg-gradient-to-l from-cyan-400 via-blue-500 to-purple-600 rounded-full shadow-[0_0_15px_rgba(0,255,255,0.6)] opacity-0 transition-all duration-500 group-hover:opacity-100 group-hover:w-[115%]" />
                                </div>
                            </div>
                        </motion.a>
                        <h1 className="text-2xl font-bold text-white mb-2 leading-tight">تسجيل الدخول إلى شبكة وتين</h1>
                        <p className="text-gray-400 text-sm">أدخل بريدك الإلكتروني للمتابعة (أو الرقم القومي)</p>
                    </motion.div>

                    <form onSubmit={handleSubmit} className="space-y-5">
                        <motion.div variants={itemVariants} className="space-y-2 text-right">
                            <label className="text-sm font-medium text-gray-300 mr-2">الحساب</label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none text-gray-500 group-focus-within:text-[#0066FF] transition-colors">
                                    <Mail size={18} />
                                </div>
                                <input
                                    type="text"
                                    required
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    className="w-full bg-white/5 border border-white/5 rounded-2xl py-3.5 pr-12 pl-4 text-white placeholder-gray-500 focus:outline-none focus:bg-white/10 focus:ring-1 focus:ring-[#0066FF]/50 transition-all shadow-inner hover:border-white/10"
                                    placeholder="الرقم القومي أو البريد"
                                    dir="rtl"
                                />
                            </div>
                        </motion.div>

                        <motion.div variants={itemVariants} className="space-y-2 text-right">
                            <label className="text-sm font-medium text-gray-300 mr-2">كلمة المرور</label>
                            <div className="relative group">
                                <div className="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none text-gray-500 group-focus-within:text-[#0066FF] transition-colors">
                                    <Lock size={18} />
                                </div>
                                <input
                                    type="password"
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full bg-white/5 border border-white/5 rounded-2xl py-3.5 pr-12 pl-4 text-white placeholder-gray-500 focus:outline-none focus:bg-white/10 focus:ring-1 focus:ring-[#0066FF]/50 transition-all shadow-inner hover:border-white/10"
                                    placeholder="••••••••"
                                    dir="ltr"
                                />
                            </div>
                        </motion.div>

                        <motion.div variants={itemVariants} className="pt-2">
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full relative group overflow-hidden rounded-xl bg-[#0066FF] hover:bg-[#0052cc] text-white font-semibold py-3.5 transition-all shadow-[0_0_20px_rgba(0,102,255,0.3)] hover:shadow-[0_0_30px_rgba(0,102,255,0.5)] disabled:opacity-70 disabled:cursor-not-allowed"
                            >
                                <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out rounded-xl" />
                                <span className="relative z-10 flex items-center justify-center gap-2">
                                    {loading ? (
                                        <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                    ) : (
                                        "تسجيل الدخول"
                                    )}
                                </span>
                            </button>
                        </motion.div>

                        <motion.div variants={itemVariants} className="relative py-4 flex items-center">
                            <div className="flex-grow border-t border-white/10"></div>
                            <span className="flex-shrink-0 mx-4 text-gray-500 text-xs">أو</span>
                            <div className="flex-grow border-t border-white/10"></div>
                        </motion.div>

                        <motion.div variants={itemVariants}>
                            <button
                                type="button"
                                className="w-full flex items-center justify-center gap-3 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-medium py-3 rounded-xl transition-all"
                            >
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M22.56 12.25C22.56 11.47 22.49 10.73 22.36 10H12V14.26H17.92C17.66 15.63 16.88 16.86 15.71 17.64V20.4H19.28C21.36 18.48 22.56 15.63 22.56 12.25Z" fill="#4285F4"/>
                                    <path d="M12 23C14.97 23 17.46 22.02 19.28 20.4L15.71 17.64C14.72 18.3 13.46 18.72 12 18.72C9.17 18.72 6.76 16.8 5.89 14.19H2.22V17.03C4.02 20.62 7.69 23 12 23Z" fill="#34A853"/>
                                    <path d="M5.89 14.19C5.67 13.52 5.54 12.78 5.54 12C5.54 11.22 5.67 10.48 5.89 9.81V6.97H2.22C1.47 8.46 1.05 10.18 1.05 12C1.05 13.82 1.47 15.54 2.22 17.03L5.89 14.19Z" fill="#FBBC05"/>
                                    <path d="M12 5.28C13.62 5.28 15.07 5.83 16.21 6.92L19.35 3.78C17.45 2 14.97 1 12 1C7.69 1 4.02 3.38 2.22 6.97L5.89 9.81C6.76 7.2 9.17 5.28 12 5.28Z" fill="#EA4335"/>
                                </svg>
                                المتابعة باستخدام Google
                            </button>
                        </motion.div>
                    </form>
                </motion.div>
            </div>

            {/* Left Half: 3D Network Globe (RTL End) */}
            <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 1.5, ease: "easeOut" }}
                className="hidden lg:flex w-full h-screen relative items-center justify-center overflow-hidden"
            >
                {/* Deep pure black vignette overlay to avoid grey borders, hiding Globe edges smoothly */}
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(0,0,0,0)_0%,rgba(0,0,0,0.9)_80%,rgba(0,0,0,1)_100%)] z-10 pointer-events-none" />
                <div className="absolute inset-0 opacity-[0.05] bg-[linear-gradient(to_right,#ffffff_1px,transparent_1px),linear-gradient(to_bottom,#ffffff_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none" />
                
                {/* Globe Component */}
                <div className="relative w-full h-full flex items-center justify-center scale-110">
                    <NetworkGlobe />
                </div>
                
                {/* Overlay Text / HUD Elements */}
                <div className="absolute bottom-12 left-12 z-20 text-left pointer-events-none">
                    <motion.div 
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 1, duration: 0.8 }}
                    >
                        <p className="text-[#0066FF] font-mono text-xs tracking-widest uppercase mb-1 flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-[#0066FF] animate-pulse" />
                            Global Node Sync
                        </p>
                        <h3 className="text-white/80 font-semibold text-lg">Wateen Infrastructure</h3>
                        <p className="text-white/40 text-sm mt-1 max-w-xs">Routing secure B2B2C medical protocols across the regional network.</p>
                    </motion.div>
                </div>
            </motion.div>
            
            <Notification />
        </div>
    );
};
