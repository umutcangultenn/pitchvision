"use client";

type VideoPlayerProps = {
  src?: string;
  title?: string;
  className?: string;
};

/**
 * HTML5 video sarmalayıcı — gerçek maç akışı URL’leri bağlandığında kullanılacak.
 */
export function VideoPlayer({
  src,
  title = "Maç videosu",
  className = "",
}: VideoPlayerProps) {
  return (
    <div
      className={`overflow-hidden rounded-xl border border-white/10 bg-black/40 ${className}`}
    >
      {src ? (
        <video
          className="aspect-video w-full"
          controls
          preload="metadata"
          title={title}
        >
          <source src={src} />
          Tarayıcınız video etiketini desteklemiyor.
        </video>
      ) : (
        <div className="flex aspect-video w-full items-center justify-center text-sm text-white/50">
          Video kaynağı atanmadı — MVP yer tutucu
        </div>
      )}
    </div>
  );
}
