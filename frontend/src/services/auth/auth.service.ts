import { defaultApiClient } from '../api/client';
import type { UserProfile, AuthTokens, ApiKeyItem } from '@/types/auth';

const TOKEN_KEY = 'fmdp_access_token';
const USER_KEY = 'fmdp_user_profile';

export class AuthService {
  constructor(private client = defaultApiClient) {
    this.client.setTokenProvider(() => this.getToken());
  }

  public getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  public getUser(): UserProfile | null {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) {
      // Default dev persona
      return {
        id: 'usr-admin-01',
        username: 'quant_admin',
        email: 'admin@fmdp.local',
        role: 'ADMIN',
        tier: 'INSTITUTIONAL',
        created_at: new Date().toISOString()
      };
    }
    try {
      return JSON.parse(raw);
    } catch {
      return null;
    }
  }

  public async login(username: string, password: string): Promise<{ user: UserProfile; tokens: AuthTokens }> {
    const raw = await this.client.post('/auth/token', { username, password });
    const res = raw?.data ?? raw ?? {};
    const tokens: AuthTokens = {
      access_token: res.access_token || '',
      refresh_token: res.refresh_token || '',
      token_type: res.token_type || 'Bearer',
      expires_in_seconds: res.expires_in ?? 900
    };

    const user: UserProfile = {
      id: res.user_id || res.jti || 'usr-session',
      username: username,
      email: `${username}@fmdp.local`,
      role: (String(res.role || 'ANALYST').toUpperCase()) as any,
      tier: (res.tier || 'INSTITUTIONAL') as any,
      created_at: new Date().toISOString()
    };

    if (tokens.access_token) {
      localStorage.setItem(TOKEN_KEY, tokens.access_token);
    }
    localStorage.setItem(USER_KEY, JSON.stringify(user));

    return { user, tokens };
  }

  public logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }

  public async getApiKeys(): Promise<ApiKeyItem[]> {
    try {
      const res = await this.client.get('/auth/api-keys');
      const items = Array.isArray(res) ? res : res.data || res.keys || [];
      return items.map((k: any) => ({
        id: k.id || k.key_id,
        name: k.name || 'Default Quant Key',
        key_prefix: k.key_prefix || 'fmdp_live_...',
        created_at: k.created_at || new Date().toISOString(),
        expires_at: k.expires_at,
        is_active: k.is_active ?? true,
        rate_limit_rpm: k.rate_limit_rpm ?? 3000
      }));
    } catch {
      return [];
    }
  }

  public async createApiKey(name: string): Promise<{ key_id: string; raw_key: string }> {
    const raw = await this.client.post('/auth/api-keys', { name });
    const data = raw?.data ?? raw ?? {};
    return {
      key_id: data.key_id || '',
      raw_key: data.api_key_once || data.raw_key || ''
    };
  }

  public async revokeApiKey(keyId: string): Promise<void> {
    await this.client.delete(`/auth/api-keys/${keyId}`);
  }
}

export const authService = new AuthService();

