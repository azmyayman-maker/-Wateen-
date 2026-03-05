import React, { useEffect, useRef, useState } from 'react';
import createGlobe from 'cobe';

export const NetworkGlobe: React.FC = () => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const pointerInteracting = useRef<number | null>(null);
    const pointerInteractionMovement = useRef(0);
    const [{ phi, theta }, setPosition] = useState({ phi: 0, theta: 0 });

    useEffect(() => {
        let currentPhi = phi;
        let currentTheta = theta;
        let width = 0;
        
        const onResize = () => {
            if (canvasRef.current) {
                width = canvasRef.current.offsetWidth;
            }
        };
        window.addEventListener('resize', onResize);
        onResize();

        if (!canvasRef.current) return;

        const globe = createGlobe(canvasRef.current, {
            devicePixelRatio: 2,
            width: width * 2,
            height: width * 2,
            phi: 0,
            theta: 0,
            dark: 1, // Enable dark mode
            diffuse: 1.2,
            mapSamples: 16000,
            mapBrightness: 6,
            baseColor: [0.05, 0.05, 0.08], // Very dark globe base
            markerColor: [1, 0.7, 0], // Urgent Amber
            glowColor: [0, 0.4, 1], // Cyan/Blue glow halo
            markers: [
                // Representative node locations (Egypt, US, Europe, Asia)
                { location: [30.0444, 31.2357], size: 0.1 }, // Cairo
                { location: [24.7136, 46.6753], size: 0.08 }, // Riyadh
                { location: [25.2048, 55.2708], size: 0.08 }, // Dubai
                { location: [51.5074, -0.1278], size: 0.05 }, // London
                { location: [40.7128, -74.0060], size: 0.06 }, // NY
                { location: [35.6762, 139.6503], size: 0.05 }, // Tokyo
            ],
            onRender: (state) => {
                // Auto-rotation physics
                if (!pointerInteracting.current) {
                    currentPhi += 0.003;
                }
                state.phi = currentPhi + pointerInteractionMovement.current;
                state.theta = currentTheta;
                state.width = width * 2;
                state.height = width * 2;
            },
        });

        return () => {
            globe.destroy();
            window.removeEventListener('resize', onResize);
        };
    }, []);

    return (
        <div style={{ width: '100%', maxWidth: 800, aspectRatio: 1, margin: 'auto', position: 'relative' }}>
            <canvas
                ref={canvasRef}
                onPointerDown={(e) => {
                    pointerInteracting.current = e.clientX;
                    if (canvasRef.current) {
                        canvasRef.current.style.cursor = 'grabbing';
                    }
                }}
                onPointerUp={() => {
                    pointerInteracting.current = null;
                    if (canvasRef.current) {
                        canvasRef.current.style.cursor = 'grab';
                    }
                }}
                onPointerOut={() => {
                    pointerInteracting.current = null;
                    if (canvasRef.current) {
                        canvasRef.current.style.cursor = 'grab';
                    }
                }}
                onMouseMove={(e) => {
                    if (pointerInteracting.current !== null) {
                        const delta = e.clientX - pointerInteracting.current;
                        pointerInteractionMovement.current = delta * 0.01;
                    }
                }}
                onTouchMove={(e) => {
                    if (pointerInteracting.current !== null && e.touches[0]) {
                        const delta = e.touches[0].clientX - pointerInteracting.current;
                        pointerInteractionMovement.current = delta * 0.01;
                    }
                }}
                style={{
                    width: '100%',
                    height: '100%',
                    cursor: 'grab',
                    contain: 'layout paint size',
                    opacity: 1,
                    transition: 'opacity 1s ease',
                }}
            />
            {/* Ambient Radial Gradient under the globe to enhance the atmosphere */}
            <div
                style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    width: '80%',
                    height: '80%',
                    transform: 'translate(-50%, -50%)',
                    background: 'radial-gradient(circle, rgba(0, 102, 255, 0.15) 0%, transparent 60%)',
                    zIndex: -1,
                    pointerEvents: 'none',
                }}
            />
        </div>
    );
};
