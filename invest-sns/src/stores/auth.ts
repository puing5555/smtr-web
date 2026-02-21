import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@/types/database';

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

interface AuthActions {
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  signup: (email: string, password: string, username: string) => Promise<void>;
}

export const useAuthStore = create<AuthState & AuthActions>()(
  persist(
    (set, get) => ({
      // State
      user: null,
      isLoading: false,
      isAuthenticated: false,

      // Actions
      setUser: (user) =>
        set({
          user,
          isAuthenticated: !!user,
        }),

      setLoading: (isLoading) => set({ isLoading }),

      login: async (email: string, password: string) => {
        set({ isLoading: true });
        try {
          // TODO: Implement Supabase login
          console.log('Login:', { email, password });
          // const { data, error } = await supabase.auth.signInWithPassword({
          //   email,
          //   password
          // });
          // if (error) throw error;
          // set({ user: data.user, isAuthenticated: true });
        } catch (error) {
          console.error('Login error:', error);
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      logout: async () => {
        set({ isLoading: true });
        try {
          // TODO: Implement Supabase logout
          // await supabase.auth.signOut();
          set({ user: null, isAuthenticated: false });
        } catch (error) {
          console.error('Logout error:', error);
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },

      signup: async (email: string, password: string, username: string) => {
        set({ isLoading: true });
        try {
          // TODO: Implement Supabase signup
          console.log('Signup:', { email, password, username });
          // const { data, error } = await supabase.auth.signUp({
          //   email,
          //   password,
          //   options: {
          //     data: { username }
          //   }
          // });
          // if (error) throw error;
        } catch (error) {
          console.error('Signup error:', error);
          throw error;
        } finally {
          set({ isLoading: false });
        }
      },
    }),
    {
      name: 'invest-sns-auth',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);