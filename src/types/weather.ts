export interface GeoLocation {
  name: string;
  latitude: number;
  longitude: number;
  country: string;
  admin1: string;  // State
  admin2: string;  // District
  admin3?: string; // Sub-district/Tehsil
  population?: number;
}

export interface WeatherData {
  region: string;
  country: string;
  state?: string;
  district?: string;
  mandal?: string;
  latitude: number;
  longitude: number;
  temperature: number;
  feelsLike: number;
  condition: string;
  conditionIcon: string;
  humidity: number;
  windSpeed: number;
  windDirection: string;
  pressure: number;
  cloudCover: number;
  localTime: string;
  lastUpdated: string;
}

export interface ForecastItem {
  day: string;
  date: string;
  high: number;
  low: number;
  condition: string;
  conditionIcon: string;
  rainChance: number;
}