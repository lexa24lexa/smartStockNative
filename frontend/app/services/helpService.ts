// frontend/app/services/helpService.ts

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

export interface HelpData {
  title: string;
  description: string;
  formula?: string;
  example?: string;
  why?: string;
  options?: string[];
  threshold?: string;
  action?: string;
  impact?: string;
  purpose?: string;
  category?: string;
}

class HelpService {
  private cache: Map<string, HelpData> = new Map();
  private allHelpCache: Record<string, HelpData> | null = null;

  async getHelp(metricKey: string): Promise<HelpData | null> {
    // Check cache first
    if (this.cache.has(metricKey)) {
      return this.cache.get(metricKey)!;
    }

    try {
      const response = await fetch(`${API_URL}/help/${metricKey}`);
      if (!response.ok) {
        throw new Error('Help data not found');
      }
      const data = await response.json();
      this.cache.set(metricKey, data);
      return data;
    } catch (error) {
      console.error(`Failed to fetch help for ${metricKey}:`, error);
      return null;
    }
  }

  async getAllHelp(): Promise<Record<string, HelpData>> {
    if (this.allHelpCache) {
      return this.allHelpCache;
    }

    try {
      const response = await fetch(`${API_URL}/help`);
      const data = await response.json();
      this.allHelpCache = data;
      
      // Populate cache
      Object.entries(data).forEach(([key, value]) => {
        this.cache.set(key, value as HelpData);
      });
      
      return data;
    } catch (error) {
      console.error('Failed to fetch all help data:', error);
      return {};
    }
  }

  async getHelpByCategory(category: string): Promise<Record<string, HelpData>> {
    try {
      const response = await fetch(`${API_URL}/help/category/${category}`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`Failed to fetch help for category ${category}:`, error);
      return {};
    }
  }

  // Précharger toutes les aides au démarrage (optionnel)
  async preload(): Promise<void> {
    await this.getAllHelp();
  }

  clearCache(): void {
    this.cache.clear();
    this.allHelpCache = null;
  }
}

export const helpService = new HelpService();