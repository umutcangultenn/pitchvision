import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { UploadDropzone } from "@/components/ui/UploadDropzone";

describe("UploadDropzone", () => {
  it("renders default title", () => {
    render(<UploadDropzone />);
    expect(screen.getByText("Video yükle")).toBeInTheDocument();
  });

  it("renders custom title", () => {
    render(<UploadDropzone title="Maç Videosu Yükle" />);
    expect(screen.getByText("Maç Videosu Yükle")).toBeInTheDocument();
  });

  it("renders file select button", () => {
    render(<UploadDropzone />);
    expect(screen.getByRole("button", { name: /dosya seç/i })).toBeInTheDocument();
  });

  it("calls onFileSelected when file is dropped", () => {
    const onFileSelected = jest.fn();
    const { container } = render(<UploadDropzone onFileSelected={onFileSelected} />);

    const dropzone = container.firstChild as HTMLElement;
    const file = new File(["video"], "match.mp4", { type: "video/mp4" });

    fireEvent.drop(dropzone, {
      dataTransfer: { files: [file] },
    });

    expect(onFileSelected).toHaveBeenCalledWith(file);
  });

  it("applies drag-over style on dragover", () => {
    const { container } = render(<UploadDropzone />);
    const dropzone = container.firstChild as HTMLElement;

    fireEvent.dragOver(dropzone, { preventDefault: () => {} });
    expect(dropzone).toHaveClass("border-accent/60");
  });

  it("removes drag-over style on dragleave", () => {
    const { container } = render(<UploadDropzone />);
    const dropzone = container.firstChild as HTMLElement;

    fireEvent.dragOver(dropzone, { preventDefault: () => {} });
    fireEvent.dragLeave(dropzone);
    expect(dropzone).not.toHaveClass("border-accent/60");
  });

  it("does not crash without onFileSelected callback", () => {
    const { container } = render(<UploadDropzone />);
    const dropzone = container.firstChild as HTMLElement;
    const file = new File(["v"], "v.mp4", { type: "video/mp4" });

    expect(() =>
      fireEvent.drop(dropzone, { dataTransfer: { files: [file] } })
    ).not.toThrow();
  });
});
