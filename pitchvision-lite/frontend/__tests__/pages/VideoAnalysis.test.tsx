import React from "react";
import { render, screen } from "@testing-library/react";

// ── Stubs ─────────────────────────────────────────────────────────────────────
jest.mock("next/link", () => {
  const Link = ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  );
  Link.displayName = "Link";
  return Link;
});

jest.mock("next/navigation", () => ({
  useParams: () => ({ id: "1001" }),
  useRouter: () => ({ push: jest.fn() }),
}));

// Recharts renders SVG — stub to avoid jsdom issues
jest.mock("recharts", () => {
  const Stub = ({ children }: { children?: React.ReactNode }) => <div>{children}</div>;
  Stub.displayName = "RechartsStub";
  return new Proxy({}, { get: () => Stub });
});

// Video element not supported in jsdom
jest.mock("@/components/video/AnalysisVideoPlayer", () => ({
  AnalysisVideoPlayer: () => <div data-testid="video-player">VideoPlayer</div>,
}));

jest.mock("@/components/analysis/VideoTimeline", () => ({
  VideoTimeline: () => <div data-testid="video-timeline">Timeline</div>,
}));

jest.mock("@/components/modals/CreateClipModal", () => ({
  CreateClipModal: () => null,
}));

jest.mock("@/components/modals/AddNoteModal", () => ({
  AddNoteModal: () => null,
}));

jest.mock("@/data/demo", () => ({
  mockMatches: [
    {
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
    },
  ],
  mockVideos: [{ id: 5001, matchId: 1001, durationSeconds: 5400, status: "ready" }],
  mockAlerts: [],
  mockClips: [],
  mockPlayers: [],
  mockPerformances: [],
  demoVideoSrc: "https://example.com/demo.mp4",
}));

import MatchAnalysisPage from "@/app/(app)/matches/[id]/analysis/page";

describe("MatchAnalysisPage (VideoAnalysis)", () => {
  it("renders without crashing", () => {
    const { container } = render(<MatchAnalysisPage />);
    expect(container).toBeTruthy();
  });

  it("renders page header with match label", () => {
    render(<MatchAnalysisPage />);
    expect(screen.getByText(/video analiz/i)).toBeInTheDocument();
  });

  it("renders video player stub", () => {
    render(<MatchAnalysisPage />);
    expect(screen.getByTestId("video-player")).toBeInTheDocument();
  });

  it("renders timeline stub", () => {
    render(<MatchAnalysisPage />);
    expect(screen.getByTestId("video-timeline")).toBeInTheDocument();
  });

  it("renders analysis tabs", () => {
    render(<MatchAnalysisPage />);
    expect(screen.getByText(/metrikler/i)).toBeInTheDocument();
    expect(screen.getByText(/uyarılar/i)).toBeInTheDocument();
    expect(screen.getByText(/klipler/i)).toBeInTheDocument();
  });

  it("renders report link", () => {
    render(<MatchAnalysisPage />);
    expect(screen.getByRole("link", { name: /raporu aç/i })).toBeInTheDocument();
  });
});
