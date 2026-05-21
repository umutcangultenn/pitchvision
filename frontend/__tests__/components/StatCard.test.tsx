import React from "react";
import { render, screen } from "@testing-library/react";
import { StatCard } from "@/components/cards/StatCard";

describe("StatCard", () => {
  it("renders title and value", () => {
    render(<StatCard title="İşlenen Maç" value="24" />);
    expect(screen.getByText("İşlenen Maç")).toBeInTheDocument();
    expect(screen.getByText("24")).toBeInTheDocument();
  });

  it("renders footer when provided", () => {
    render(<StatCard title="Oyuncu" value="186" footer="+3 bu hafta" />);
    expect(screen.getByText("+3 bu hafta")).toBeInTheDocument();
  });

  it("does not render footer when omitted", () => {
    const { container } = render(<StatCard title="Oyuncu" value="186" />);
    // footer div should not exist
    expect(container.querySelectorAll("div").length).toBeGreaterThan(0);
    expect(screen.queryByText("+3 bu hafta")).not.toBeInTheDocument();
  });

  it.each([
    ["accent",   "border-accent/30"],
    ["success",  "border-success/30"],
    ["warning",  "border-warning/30"],
    ["danger",   "border-danger/30"],
  ] as const)("applies %s tone class", (tone, cls) => {
    const { container } = render(<StatCard title="T" value="V" tone={tone} />);
    expect(container.firstChild).toHaveClass(cls);
  });
});
