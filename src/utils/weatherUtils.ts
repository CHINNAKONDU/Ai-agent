import { WeatherData, ForecastItem } from "../types/weather";

const conditions = [
  { name: "Sunny", icon: "☀️" },
  { name: "Partly Cloudy", icon: "⛅" },
  { name: "Cloudy", icon: "☁️" },
  { name: "Overcast", icon: "🌥️" },
  { name: "Light Rain", icon: "🌧️" },
  { name: "Heavy Rain", icon: "🌧️" },
  { name: "Thunderstorm", icon: "⛈️" },
  { name: "Snow", icon: "🌨️" },
  { name: "Fog", icon: "🌫️" },
  { name: "Clear", icon: "🌙" },
];

const countries = [
  "United States", "United Kingdom", "Canada", "Australia", 
  "Germany", "France", "Japan", "India", "Brazil", "Mexico"
];

const windDirections = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"];

// Simple hash function to generate consistent random values
function hashString(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash);
}

function seededRandom(seed: number, min: number, max: number): number {
  const x = Math.sin(seed) * 10000;
  const random = x - Math.floor(x);
  return Math.floor(random * (max - min + 1)) + min;
}

export function generateWeatherData(region: string): WeatherData {
  const hash = hashString(region.toLowerCase());
  
  const temp = seededRandom(hash, -10, 40);
  const conditionIndex = seededRandom(hash + 1, 0, conditions.length - 1);
  const countryIndex = seededRandom(hash + 2, 0, countries.length - 1);
  
  const now = new Date();
  const hours = now.getHours();
  
  // Adjust condition based on temperature
  let condition = conditions[conditionIndex];
  if (temp < 0) {
    condition = conditions[7]; // Snow
  } else if (temp > 30 && conditionIndex < 4) {
    condition = conditions[0]; // Sunny
  }
  
  return {
    region: region.charAt(0).toUpperCase() + region.slice(1),
    country: countries[countryIndex],
    temperature: temp,
    feelsLike: temp + seededRandom(hash + 3, -3, 5),
    condition: condition.name,
    conditionIcon: condition.icon,
    humidity: seededRandom(hash + 4, 30, 95),
    windSpeed: seededRandom(hash + 5, 5, 50),
    windDirection: windDirections[seededRandom(hash + 6, 0, 7)],
    pressure: seededRandom(hash + 7, 990, 1030),
    visibility: seededRandom(hash + 8, 5, 20),
    uvIndex: seededRandom(hash + 9, 1, 11),
    cloudCover: seededRandom(hash + 10, 0, 100),
    localTime: `${hours.toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`,
    lastUpdated: new Date().toLocaleTimeString(),
  };
}

export function generateForecast(): ForecastItem[] {
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const today = new Date().getDay();
  
  return Array.from({ length: 5 }, (_, i) => {
    const dayIndex = (today + i + 1) % 7;
    const conditionIndex = Math.floor(Math.random() * conditions.length);
    const condition = conditions[conditionIndex];
    
    return {
      day: days[dayIndex],
      high: Math.floor(Math.random() * 20) + 15,
      low: Math.floor(Math.random() * 10) + 5,
      condition: condition.name,
      conditionIcon: condition.icon,
      rainChance: Math.floor(Math.random() * 100),
    };
  });
}