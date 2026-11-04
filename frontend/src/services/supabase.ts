import { createClient, SupabaseClient } from '@supabase/supabase-js';

export const SUPABASE_URL = 
  import.meta.env.VITE_SUPABASE_URL || 'https://bhnrrosrjednzctdirkn.supabase.co';

export const SUPABASE_ANON_KEY = 
  import.meta.env.VITE_SUPABASE_ANON_KEY || 'sb_publishable_UEgdn1EB40terFHDApHIYQ_tr3ZQATH';

export const supabase: SupabaseClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
  },
});

export interface SupabaseHealth {
  connected: boolean;
  url: string;
  tablesFound: boolean;
  message: string;
}

export async function checkSupabaseHealth(): Promise<SupabaseHealth> {
  try {
    const { data, error } = await supabase.from('workers').select('worker_id').limit(1);

    if (error) {
      if (error.code === 'PGRST205' || error.message?.includes('schema cache')) {
        return {
          connected: true,
          url: SUPABASE_URL,
          tablesFound: false,
          message: 'Connected to Supabase. Schema tables pending execution in SQL Editor.',
        };
      }
      return {
        connected: false,
        url: SUPABASE_URL,
        tablesFound: false,
        message: error.message || 'Supabase API query error',
      };
    }

    return {
      connected: true,
      url: SUPABASE_URL,
      tablesFound: true,
      message: 'Connected & Synced with Supabase PostgreSQL (public.workers schema active).',
    };
  } catch (err: any) {
    return {
      connected: false,
      url: SUPABASE_URL,
      tablesFound: false,
      message: err.message || 'Unable to connect to Supabase endpoint',
    };
  }
}
