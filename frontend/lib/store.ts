import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { AuthUser } from "@/lib/api";
import { setAuthToken, clearAuthToken } from "@/lib/api";

type AuthState = {
  isAuthenticated: boolean;
  user: AuthUser | null;
  // Login: token'ı localStorage'a yazar, state'i günceller
  login: (token: string, user: AuthUser) => void;
  // Logout: token'ı siler, state'i sıfırlar
  logout: () => void;
  // Geriye dönük uyumluluk için
  setAuthenticated: (value: boolean) => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      user: null,

      login: (token, user) => {
        setAuthToken(token);
        set({ isAuthenticated: true, user });
      },

      logout: () => {
        clearAuthToken();
        set({ isAuthenticated: false, user: null });
      },

      setAuthenticated: (value) => set({ isAuthenticated: value }),
    }),
    {
      name: "pv-auth",
      // Sadece user bilgisini persist et, token zaten localStorage'da
      partialize: (state) => ({ isAuthenticated: state.isAuthenticated, user: state.user }),
    },
  ),
);
