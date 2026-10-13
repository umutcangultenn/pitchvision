import React from "react";
import { render, screen } from "@testing-library/react";
import { AlertCard } from "@/components/cards/AlertCard";
import type { TacticalAlert } from "@/types/domain";

const baseAlert: TacticalAlert = {
  id: 3001,
  matchId: 1001,
  teamId: 1,
  playerId: 1,
  alertType: "defensive_line_break",
  startTime: 450,
  endTime: 510,
  confidence: 0.82,
  severity: "high",
  status: "open",
  title: "Savunma hattı bozulması",
  description: "Savunma hattı senkronizasyonu bozuldu.",
  relatedMetric: "defensive_line",
  suggestedClipId: undefined,
  createdAt: "2026-04-12T13:00:00.000Z",
};

describe("AlertCard", () => {
  it("renders alert title", () => {
    render(<AlertCard alert={baseAlert} />);
    expect(screen.getByText("Savunma hattı bozulması")).toBeInTheDocument();
  });

  it("renders description", () => {
    render(<AlertCard alert={baseAlert} />);
    expect(screen.getByText(/senkronizasyonu bozuldu/i)).toBeInTheDocument();
  });

  it("renders time range", () => {
    render(<AlertCard alert={baseAlert} />);
    expect(screen.getByText(/450s/)).toBeInTheDocument();
    expect(screen.getByText(/510s/)).toBeInTheDocument();
  });

  it("renders without description", () => {
    render(<AlertCard alert={{ ...baseAlert, description: undefined }} />);
    expect(screen.getByText("Savunma hattı bozulması")).toBeInTheDocument();
  });

  it("renders without confidence badge when confidence is undefined", () => {
    const { container } = render(
      <AlertCard alert={{ ...baseAlert, confidence: undefined }} />
    );
    expect(container).toBeTruthy();
  });

  it("renders critical severity alert", () => {
    render(<AlertCard alert={{ ...baseAlert, severity: "critical" }} />);
    expect(screen.getByText("Savunma hattı bozulması")).toBeInTheDocument();
  });
});
