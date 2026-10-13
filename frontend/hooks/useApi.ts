"use client";

/**
 * useApi — generic data-fetching hook
 *
 * Kullanım:
 *   const { data, loading, error, refetch } = useApi(
 *     () => apiGetMatches(),
 *     { deps: [teamId] }
 *   );
 */

import { useCallback, useEffect, useRef, useState } from "react";
import type { ApiResult } from "@/lib/api";

type UseApiOptions<T> = {
  /** useEffect dependency array — değişince yeniden fetch yapar */
  deps?: unknown[];
  /** İlk render'da fetch yapma */
  skip?: boolean;
  /** Başarılı fetch sonrası callback */
  onSuccess?: (data: T) => void;
  /** Hata sonrası callback */
  onError?: (error: { status: number | "network" | "parse"; message: string }) => void;
};

type UseApiState<T> = {
  data: T | null;
  loading: boolean;
  error: { status: number | "network" | "parse"; message: string } | null;
  /** Manuel yeniden fetch */
  refetch: () => void;
};

export function useApi<T>(
  fetcher: () => Promise<ApiResult<T>>,
  options: UseApiOptions<T> = {},
): UseApiState<T> {
  const { deps = [], skip = false, onSuccess, onError } = options;

  const [data, setData]       = useState<T | null>(null);
  const [loading, setLoading] = useState(!skip);
  const [error, setError]     = useState<UseApiState<T>["error"]>(null);

  // Stale closure koruması
  const fetcherRef  = useRef(fetcher);
  const onSuccessRef = useRef(onSuccess);
  const onErrorRef   = useRef(onError);
  fetcherRef.current   = fetcher;
  onSuccessRef.current = onSuccess;
  onErrorRef.current   = onError;

  const [tick, setTick] = useState(0);
  const refetch = useCallback(() => setTick((n) => n + 1), []);

  useEffect(() => {
    if (skip) return;
    let cancelled = false;

    setLoading(true);
    setError(null);

    fetcherRef.current().then((result) => {
      if (cancelled) return;
      setLoading(false);
      if (result.ok) {
        setData(result.data);
        onSuccessRef.current?.(result.data);
      } else {
        setError(result.error);
        onErrorRef.current?.(result.error);
      }
    });

    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [skip, tick, ...deps]);

  return { data, loading, error, refetch };
}

/** Mutation hook — POST/PATCH/DELETE için */
type UseMutationState<TInput, TOutput> = {
  mutate: (input: TInput) => Promise<ApiResult<TOutput>>;
  loading: boolean;
  error: UseApiState<TOutput>["error"] | null;
  data: TOutput | null;
  reset: () => void;
};

export function useMutation<TInput, TOutput>(
  mutator: (input: TInput) => Promise<ApiResult<TOutput>>,
  options: { onSuccess?: (data: TOutput) => void; onError?: (err: UseApiState<TOutput>["error"]) => void } = {},
): UseMutationState<TInput, TOutput> {
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState<UseApiState<TOutput>["error"]>(null);
  const [data, setData]       = useState<TOutput | null>(null);

  const mutatorRef = useRef(mutator);
  mutatorRef.current = mutator;

  const mutate = useCallback(async (input: TInput): Promise<ApiResult<TOutput>> => {
    setLoading(true);
    setError(null);
    const result = await mutatorRef.current(input);
    setLoading(false);
    if (result.ok) {
      setData(result.data);
      options.onSuccess?.(result.data);
    } else {
      setError(result.error);
      options.onError?.(result.error);
    }
    return result;
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const reset = useCallback(() => { setData(null); setError(null); setLoading(false); }, []);

  return { mutate, loading, error, data, reset };
}
