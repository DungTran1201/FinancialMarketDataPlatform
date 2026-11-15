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
    const res = await this.client.post('/auth/token', { username, password });
    const tokens: AuthTokens = {
      access_token: res.access_token || 'mock_access_token',
      refresh_token: res.refresh_token || 'mock_refresh_token',
      token_type: res.token_type || 'Bearer',
      expires_in_seconds: res.expires_in ?? 3600
    };

    const user: UserProfile = {
      id: res.user_id || 'usr-admin-01',
      username: username,
      email: `${username}@fmdp.local`,
      role: (res.role || 'ADMIN') as any,
      tier: (res.tier || 'INSTITUTIONAL') as any,
      created_at: new Date().toISOString()
    };

    localStorage.setItem(TOKEN_KEY, tokens.access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));

    return { user, tokens };
  }

  public logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }

  public async getApiKeys(): Promise<ApiKeyItem[]> {
    const res = await this.client.get('/auth/api-keys');
    const items = Array.isArray(res) ? res : res.keys || [];
    return items.map((k: any) => ({
      id: k.id || k.key_id,
      name: k.name || 'Default Quant Key',
      key_prefix: k.key_prefix || 'fmdp_live_...',
      created_at: k.created_at || new Date().toISOString(),
      expires_at: k.expires_at,
      is_active: k.is_active ?? true,
      rate_limit_rpm: k.rate_limit_rpm ?? 3000
    }));
  }

  public async createApiKey(name: string): Promise<{ key_id: string; raw_key: string }> {
    return await this.client.post('/auth/api-keys', { name });
  }

  public async revokeApiKey(keyId: string): Promise<void> {
    await this.client.delete(`/auth/api-keys/${keyId}`);
  }
}

export const authService = new AuthService();

