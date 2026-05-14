import React from "react";
import { render, screen } from "@testing-library/react";
import { PlayerCard } from "@/components/cards/PlayerCard";
import type { Player } from "@/types/domain";

const basePlayer: Player = {
  id: 1,
  organizationId: 1,
  teamId: 1,
  firstName: "Arda",
  lastName: "Yılmaz",
  birthDate: "2011-03-14",
  position: "CM",
  dominantFoot: "right",
  heightCm: 168,
  weightKg: 58,
  technicalScore: 7.4,
  tacticalScore: 7.1,
  physicalScore: 6.8,
  decisionScore: 7.0,
  developmentVelocity: 0.52,
  createdAt: "2026-01-01T00:00:00.000Z",
};

describe("PlayerCard", () => {
  it("renders full name", () => {
    render(<PlayerCard player={basePlayer} />);
    expect(screen.getByText("Arda Yılmaz")).toBeInTheDocument();
  });

  it("renders position", () => {
    render(<PlayerCard player={basePlayer} />);
    expect(screen.getByText("CM")).toBeInTheDocument();
  });

  it("renders technical score", () => {
    render(<PlayerCard player={basePlayer} />);
    expect(screen.getByText("7.4")).toBeInTheDocument();
  });

  it("renders tactical score", () => {
    render(<PlayerCard player={basePlayer} />);
    expect(screen.getByText("7.1")).toBeInTheDocument();
  });

  it("renders development velocity", () => {
    render(<PlayerCard player={basePlayer} />);
    expect(screen.getByText("0.52")).toBeInTheDocument();
  });

  it("renders — when scores are undefined", () => {
    render(
      <PlayerCard
        player={{ ...basePlayer, technicalScore: undefined, tacticalScore: undefined }}
      />
    );
    expect(screen.getAllByText("—").length).toBeGreaterThanOrEqual(2);
  });

  it("renders dominant foot", () => {
    render(<PlayerCard player={basePlayer} />);
    expect(screen.getByText("right")).toBeInTheDocument();
  });
});
