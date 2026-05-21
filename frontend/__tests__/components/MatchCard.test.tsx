import React from "react";
import { render, screen } from "@testing-library/react";
import { MatchCard } from "@/components/cards/MatchCard";
import type { Match } from "@/types/domain";

// next/link stub
jest.mock("next/link", () => {
  const Link = ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  );
  Link.displayName = "Link";
  return Link;
});

const baseMatch: Match = {
  id: 1001,
  organizationId: 1,
  teamId: 1,
  opponentName: "Mavi Spor",
  matchDate: "2026-04-12T13:00:00.000Z",
  ageCategory: "U15",
  gameFormat: "11v11",
  pitchLength: 105,
  pitchWidth: 68,
  firstHalfAttackDirection: "left_to_right",
  scoreFor: 3,
  scoreAgainst: 1,
  videoSource: "file_upload",
  status: "completed",
  createdAt: "2026-04-12T13:00:00.000Z",
};

describe("MatchCard", () => {
  it("renders opponent name", () => {
    render(<MatchCard match={baseMatch} />);
    expect(screen.getByText("Mavi Spor")).toBeInTheDocument();
  });

  it("renders score", () => {
    render(<MatchCard match={baseMatch} />);
    expect(screen.getByText("3:1")).toBeInTheDocument();
  });

  it("renders age category and game format", () => {
    render(<MatchCard match={baseMatch} />);
    expect(screen.getByText("U15")).toBeInTheDocument();
    expect(screen.getByText("11v11")).toBeInTheDocument();
  });

  it("uses detailHref when provided", () => {
    render(<MatchCard match={baseMatch} detailHref="/matches/1001/analysis" />);
    const link = screen.getByRole("link", { name: /detay/i });
    expect(link).toHaveAttribute("href", "/matches/1001/analysis");
  });

  it("falls back to default href", () => {
    render(<MatchCard match={baseMatch} />);
    const link = screen.getByRole("link", { name: /detay/i });
    expect(link).toHaveAttribute("href", "/matches/1001");
  });

  it("renders processing status match", () => {
    render(<MatchCard match={{ ...baseMatch, status: "processing" }} />);
    expect(screen.getByText("Mavi Spor")).toBeInTheDocument();
  });
});
