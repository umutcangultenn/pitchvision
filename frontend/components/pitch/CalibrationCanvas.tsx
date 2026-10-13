"use client";

import React, { useRef, useEffect, useState, useCallback } from "react";
import type { CalibrationPoint, CalibrationResult } from "@/types/domain";

type CalibrationCanvasProps = {
  className?: string;
  onPointsChange?: (points: CalibrationPoint[]) => void;
  onResultChange?: (result: CalibrationResult | null) => void;
};

// Kalibrasyon noktaları tanımları
const CALIBRATION_POINTS: Omit<CalibrationPoint, "x" | "y" | "isMarked">[] = [
  { id: "corner-tl", label: "Sol üst köşe", description: "Saha sol üst köşe noktası", fieldX: 0, fieldY: 0, isRequired: true },
  { id: "corner-tr", label: "Sağ üst köşe", description: "Saha sağ üst köşe noktası", fieldX: 105, fieldY: 0, isRequired: true },
  { id: "corner-bl", label: "Sol alt köşe", description: "Saha sol alt köşe noktası", fieldX: 0, fieldY: 68, isRequired: true },
  { id: "corner-br", label: "Sağ alt köşe", description: "Saha sağ alt köşe noktası", fieldX: 105, fieldY: 68, isRequired: true },
  { id: "center", label: "Orta nokta", description: "Saha merkez noktası", fieldX: 52.5, fieldY: 34, isRequired: false },
  { id: "penalty-tl", label: "Ceza sahası sol üst", description: "Sol ceza sahası üst köşesi", fieldX: 16.5, fieldY: 13.84, isRequired: false },
  { id: "penalty-tr", label: "Ceza sahası sağ üst", description: "Sağ ceza sahası üst köşesi", fieldX: 88.5, fieldY: 13.84, isRequired: false },
  { id: "penalty-spot", label: "Penaltı noktası", description: "Penaltı atış noktası", fieldX: 52.5, fieldY: 11, isRequired: false },
];

export function CalibrationCanvas({ className = "", onPointsChange, onResultChange }: CalibrationCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [points, setPoints] = useState<CalibrationPoint[]>(
    CALIBRATION_POINTS.map(p => ({ ...p, isMarked: false }))
  );
  const [selectedPoint, setSelectedPoint] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });

  // Canvas boyutları
  const canvasWidth = 800;
  const canvasHeight = 450;

  // Pitch field çizimi
  const drawPitchField = useCallback((ctx: CanvasRenderingContext2D) => {
    const { width, height } = ctx.canvas;
    
    // Arka plan
    ctx.fillStyle = "#0d4d3d";
    ctx.fillRect(0, 0, width, height);
    
    // Saha çizgileri
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 2;
    
    // Dış çerçeve
    ctx.strokeRect(50, 50, width - 100, height - 100);
    
    // Orta çizgi
    ctx.beginPath();
    ctx.moveTo(width / 2, 50);
    ctx.lineTo(width / 2, height - 50);
    ctx.stroke();
    
    // Orta daire
    ctx.beginPath();
    ctx.arc(width / 2, height / 2, 60, 0, 2 * Math.PI);
    ctx.stroke();
    
    // Ceza sahaları
    const penaltyWidth = 120;
    const penaltyHeight = 80;
    
    // Sol ceza sahası
    ctx.strokeRect(50, (height - penaltyHeight) / 2, penaltyWidth, penaltyHeight);
    
    // Sağ ceza sahası
    ctx.strokeRect(width - 50 - penaltyWidth, (height - penaltyHeight) / 2, penaltyWidth, penaltyHeight);
    
    // Penaltı noktaları
    ctx.fillStyle = "#ffffff";
    ctx.beginPath();
    ctx.arc(50 + 80, height / 2, 3, 0, 2 * Math.PI);
    ctx.fill();
    
    ctx.beginPath();
    ctx.arc(width - 50 - 80, height / 2, 3, 0, 2 * Math.PI);
    ctx.fill();
  }, []);

  // Noktaları çizme
  const drawPoints = useCallback((ctx: CanvasRenderingContext2D) => {
    points.forEach(point => {
      if (!point.isMarked || point.x === undefined || point.y === undefined) return;
      
      const isSelected = selectedPoint === point.id;
      const radius = isSelected ? 8 : 6;
      
      // Nokta gölgesi
      ctx.fillStyle = "rgba(0, 0, 0, 0.3)";
      ctx.beginPath();
      ctx.arc(point.x + 2, point.y + 2, radius, 0, 2 * Math.PI);
      ctx.fill();
      
      // Nokta
      ctx.fillStyle = point.isRequired ? "#0ea5a2" : "#34d399";
      ctx.beginPath();
      ctx.arc(point.x, point.y, radius, 0, 2 * Math.PI);
      ctx.fill();
      
      // Seçili nokta için ring
      if (isSelected) {
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(point.x, point.y, radius + 3, 0, 2 * Math.PI);
        ctx.stroke();
      }
      
      // Label
      ctx.fillStyle = "#ffffff";
      ctx.font = "12px system-ui";
      ctx.textAlign = "center";
      ctx.fillText(point.label, point.x, point.y - 15);
    });
  }, [points, selectedPoint]);

  // Canvas çizimi
  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    
    // Temizle
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Transform uygula
    ctx.save();
    ctx.translate(pan.x, pan.y);
    ctx.scale(zoom, zoom);
    
    // Saha çiz
    drawPitchField(ctx);
    
    // Noktaları çiz
    drawPoints(ctx);
    
    ctx.restore();
  }, [drawPitchField, drawPoints, zoom, pan]);

  // Canvas event handlers
  const getMousePos = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    return {
      x: ((e.clientX - rect.left) * scaleX - pan.x) / zoom,
      y: ((e.clientY - rect.top) * scaleY - pan.y) / zoom
    };
  }, [pan, zoom]);

  const handleMouseDown = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const pos = getMousePos(e);
    
    // Mevcut nokta seçimi kontrolü
    const clickedPoint = points.find(p => {
      if (!p.isMarked || p.x === undefined || p.y === undefined) return false;
      const distance = Math.sqrt((p.x - pos.x) ** 2 + (p.y - pos.y) ** 2);
      return distance <= 10;
    });
    
    if (clickedPoint) {
      setSelectedPoint(clickedPoint.id);
      setIsDragging(true);
    } else {
      // Yeni nokta ekleme (seçili nokta varsa)
      if (selectedPoint) {
        setPoints(prev => prev.map(p => 
          p.id === selectedPoint 
            ? { ...p, x: pos.x, y: pos.y, isMarked: true }
            : p
        ));
      }
    }
  }, [getMousePos, points, selectedPoint]);

  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDragging || !selectedPoint) return;
    
    const pos = getMousePos(e);
    setPoints(prev => prev.map(p => 
      p.id === selectedPoint 
        ? { ...p, x: pos.x, y: pos.y }
        : p
    ));
  }, [isDragging, selectedPoint, getMousePos]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Zoom kontrolü
  const handleZoom = useCallback((delta: number) => {
    setZoom(prev => Math.max(0.5, Math.min(3, prev + delta)));
  }, []);

  // Kalibrasyon hesaplama (mock)
  const calculateCalibration = useCallback((): CalibrationResult | null => {
    const markedPoints = points.filter(p => p.isMarked);
    const requiredPoints = points.filter(p => p.isRequired && p.isMarked);
    
    if (requiredPoints.length < 4) return null;
    
    // Mock hesaplama
    const errorBase = Math.max(0, 4 - requiredPoints.length) * 0.5;
    const errorRandom = Math.random() * 0.3;
    const averageError = errorBase + errorRandom;
    
    let quality: CalibrationResult["quality"];
    if (averageError < 0.5) quality = "excellent";
    else if (averageError < 1.0) quality = "good";
    else if (averageError < 2.0) quality = "fair";
    else quality = "poor";
    
    return {
      averageError: Number(averageError.toFixed(2)),
      quality,
      pointCount: markedPoints.length,
      homographyMatrix: [[1, 0, 0], [0, 1, 0], [0, 0, 1]] // Mock matrix
    };
  }, [points]);

  // Effects
  useEffect(() => {
    draw();
  }, [draw]);

  useEffect(() => {
    onPointsChange?.(points);
    const result = calculateCalibration();
    onResultChange?.(result);
  }, [points, onPointsChange, onResultChange, calculateCalibration]);

  return (
    <div ref={containerRef} className={`space-y-4 ${className}`}>
      {/* Canvas kontrolleri */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleZoom(-0.2)}
            className="px-3 py-1.5 rounded-lg text-xs font-medium bg-white/10 border border-white/20 text-text hover:bg-white/15 transition-all"
          >
            🔍−
          </button>
          <span className="text-xs text-text-muted px-2">{Math.round(zoom * 100)}%</span>
          <button
            onClick={() => handleZoom(0.2)}
            className="px-3 py-1.5 rounded-lg text-xs font-medium bg-white/10 border border-white/20 text-text hover:bg-white/15 transition-all"
          >
            🔍+
          </button>
        </div>
        <div className="text-xs text-text-muted">
          {selectedPoint ? "Noktayı yerleştirmek için tıklayın" : "Bir nokta seçin"}
        </div>
      </div>

      {/* Canvas */}
      <div className="rounded-xl border border-white/10 bg-black/30 p-2 overflow-hidden">
        <canvas
          ref={canvasRef}
          width={canvasWidth}
          height={canvasHeight}
          className={`w-full h-auto max-w-full rounded-lg ${
            selectedPoint ? "cursor-crosshair" : "cursor-pointer"
          }`}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        />
      </div>
    </div>
  );
}
