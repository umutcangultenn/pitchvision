import { create } from "zustand";

type AuthState = {
  /** MVP: gerçek JWT / oturum gelene kadar bayrak */
  isAuthenticated: boolean;
  setAuthenticated: (value: boolean) => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  setAuthenticated: (value) => set({ isAuthenticated: value }),
}));
