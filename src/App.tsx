import { useState } from "react";
import { Search, MapPin, AlertCircle, Locate } from "lucide-react";
import { WeatherCard } from "./components/WeatherCard";
import { WeatherDetails } from "./components/WeatherDetails";
import { ForecastCard } from "./components/ForecastCard";
import { WeatherData, ForecastItem, GeoLocation } from "./types/weather";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";

function App() {
  const [region, setRegion] = useState("");
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [forecast, setForecast] = useState<ForecastItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [locationInfo, setLocationInfo] = useState<GeoLocation | null>(null);

  // Fetch coordinates from location name
  const fetchCoordinates = async (location: string): Promise<GeoLocation | null> => {
    try {
      const response = await fetch(
        `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(location)}&count=5&language=en&format=json`
      );
      const data = await response.json();
      
      if (data.results && data.results.length > 0) {
        // Find best match for Indian locations
        const bestMatch = data.results.find((r: any) => 
          r.country === "India" || r.country_code === "IN"
        ) || data.results[0];
        
        return {
          name: bestMatch.name,
          latitude: bestMatch.latitude,
          longitude: bestMatch.longitude,
          country: bestMatch.country || "",
          admin1: bestMatch.admin1 || "", // State
          admin2: bestMatch.admin2 || "", // District/Mandal
          admin3: bestMatch.admin3 || "",
          population: bestMatch.population,
        };
      }
      return null;
    } catch (err) {
      console.error("Geocoding error:", err);
      return null;
    }
  };

  // Fetch weather data from Open-Meteo API
  const fetchWeatherData = async (geo: GeoLocation): Promise<{ weather: WeatherData; forecast: ForecastItem[] } | null> => {
    try {
      const response = await fetch(
        `https://api.open-meteo.com/v1/forecast?latitude=${geo.latitude}&longitude=${geo.longitude}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,pressure_msl,cloud_cover&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto&forecast_days=5`
      );
      const data = await response.json();
      
      if (!data.current || !data.daily) {
        return null;
      }

      const weatherCodeMap: Record<number, { condition: string; icon: string }> = {
        0: { condition: "Clear Sky", icon: "☀️" },
        1: { condition: "Mainly Clear", icon: "🌤️" },
        2: { condition: "Partly Cloudy", icon: "⛅" },
        3: { condition: "Overcast", icon: "☁️" },
        45: { condition: "Foggy", icon: "🌫️" },
        48: { condition: "Depositing Rime Fog", icon: "🌫️" },
        51: { condition: "Light Drizzle", icon: "🌧️" },
        53: { condition: "Moderate Drizzle", icon: "🌧️" },
        55: { condition: "Dense Drizzle", icon: "🌧️" },
        61: { condition: "Slight Rain", icon: "🌧️" },
        63: { condition: "Moderate Rain", icon: "🌧️" },
        65: { condition: "Heavy Rain", icon: "🌧️" },
        71: { condition: "Slight Snow", icon: "🌨️" },
        73: { condition: "Moderate Snow", icon: "🌨️" },
        75: { condition: "Heavy Snow", icon: "🌨️" },
        77: { condition: "Snow Grains", icon: "🌨️" },
        80: { condition: "Slight Rain Showers", icon: "🌦️" },
        81: { condition: "Moderate Rain Showers", icon: "🌦️" },
        82: { condition: "Violent Rain Showers", icon: "⛈️" },
        85: { condition: "Slight Snow Showers", icon: "🌨️" },
        86: { condition: "Heavy Snow Showers", icon: "🌨️" },
        95: { condition: "Thunderstorm", icon: "⛈️" },
        96: { condition: "Thunderstorm with Hail", icon: "⛈️" },
        99: { condition: "Thunderstorm with Heavy Hail", icon: "⛈️" },
      };

      const code = data.current.weather_code;
      const weatherInfo = weatherCodeMap[code] || { condition: "Unknown", icon: "🌡️" };

      const getWindDirection = (degrees: number): string => {
        const directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"];
        return directions[Math.round(degrees / 45) % 8];
      };

      const weather: WeatherData = {
        region: geo.name,
        country: geo.country,
        state: geo.admin1,
        district: geo.admin2,
        mandal: geo.name,
        latitude: geo.latitude,
        longitude: geo.longitude,
        temperature: Math.round(data.current.temperature_2m),
        feelsLike: Math.round(data.current.apparent_temperature),
        condition: weatherInfo.condition,
        conditionIcon: weatherInfo.icon,
        humidity: data.current.relative_humidity_2m,
        windSpeed: Math.round(data.current.wind_speed_10m),
        windDirection: getWindDirection(data.current.wind_direction_10m),
        pressure: Math.round(data.current.pressure_msl),
        cloudCover: data.current.cloud_cover,
        localTime: new Date().toLocaleTimeString("en-US", { 
          hour: "2-digit", 
          minute: "2-digit",
          hour12: true 
        }),
        lastUpdated: new Date().toLocaleString(),
      };

      const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
      const forecast: ForecastItem[] = data.daily.time.map((date: string, index: number) => {
        const d = new Date(date);
        const dayCode = data.daily.weather_code[index];
        const dayWeather = weatherCodeMap[dayCode] || { condition: "Unknown", icon: "🌡️" };
        
        return {
          day: days[d.getDay()],
          date: d.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
          high: Math.round(data.daily.temperature_2m_max[index]),
          low: Math.round(data.daily.temperature_2m_min[index]),
          condition: dayWeather.condition,
          conditionIcon: dayWeather.icon,
          rainChance: data.daily.precipitation_probability_max[index] || 0,
        };
      });

      return { weather, forecast };
    } catch (err) {
      console.error("Weather fetch error:", err);
      return null;
    }
  };

  const handleSearch = async () => {
    if (!region.trim()) {
      setError("Please enter a Mandal or region name");
      return;
    }

    setIsLoading(true);
    setError("");
    setWeather(null);
    setForecast([]);
    setLocationInfo(null);

    const geo = await fetchCoordinates(region);
    
    if (!geo) {
      setError(`Could not find location "${region}". Try format: "Mandal Name, District, State, India"`);
      setIsLoading(false);
      return;
    }

    setLocationInfo(geo);

    const result = await fetchWeatherData(geo);
    
    if (!result) {
      setError("Failed to fetch weather data. Please try again.");
      setIsLoading(false);
      return;
    }

    setWeather(result.weather);
    setForecast(result.forecast);
    setIsLoading(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold text-white tracking-tight">
            <span className="text-emerald-400">Mandal</span>Weather
          </h1>
          <div className="text-slate-400 text-sm hidden sm:block">
            Mandal-Level Weather Conditions
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        {/* Search Section */}
        <div className="bg-slate-800 rounded-2xl p-6 mb-8 border border-slate-700 shadow-xl">
          <div className="mb-4">
            <h2 className="text-white font-semibold text-lg mb-1">Search by Mandal</h2>
            <p className="text-slate-400 text-sm">Enter Mandal name to check weather conditions</p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Input
                type="text"
                placeholder="Enter Mandal name (e.g., Lakkireddipalle, Kadapa)"
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                onKeyDown={handleKeyPress}
                className="bg-slate-700 border-slate-600 text-white placeholder-slate-400 text-lg py-6 px-6 pr-12 rounded-xl focus:border-emerald-500 focus:ring-emerald-500"
              />
              <Search className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
            </div>
            <Button
              onClick={handleSearch}
              disabled={isLoading}
              className="bg-emerald-500 hover:bg-emerald-600 text-white font-semibold px-8 py-6 rounded-xl text-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Loading...
                </div>
              ) : (
                "Check Weather"
              )}
            </Button>
          </div>
          
          {/* Location Found Info */}
          {locationInfo && !isLoading && (
            <div className="mt-4 bg-slate-700/50 rounded-xl p-4 border border-slate-600">
              <div className="flex items-start gap-2 text-emerald-400">
                <Locate className="w-5 h-5 mt-0.5 flex-shrink-0" />
                <div>
                  <span className="font-semibold">Location Found:</span>
                  <div className="text-white mt-1">
                    <span className="font-medium">{locationInfo.name}</span>
                    {locationInfo.admin2 && <span className="text-slate-300"> (District: {locationInfo.admin2})</span>}
                    {locationInfo.admin1 && <span className="text-slate-400">, {locationInfo.admin1}</span>}
                    {locationInfo.country && <span className="text-slate-500">, {locationInfo.country}</span>}
                  </div>
                  <div className="text-slate-400 text-xs mt-1">
                    Coordinates: {locationInfo.latitude.toFixed(4)}°N, {locationInfo.longitude.toFixed(4)}°E
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {error && (
            <div className="mt-4 flex items-center gap-2 text-red-400 bg-red-500/10 rounded-lg p-3">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <p className="text-sm">{error}</p>
            </div>
          )}
        </div>

        {/* Weather Results */}
        {weather && (
          <div className="space-y-6">
            {/* Main Weather Card */}
            <WeatherCard weather={weather} />

            {/* Weather Details Grid */}
            <WeatherDetails weather={weather} />

            {/* 5-Day Forecast */}
            <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700">
              <h2 className="text-xl font-semibold text-white mb-4">
                5-Day Forecast
              </h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
                {forecast.map((item, index) => (
                  <ForecastCard key={index} forecast={item} />
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!weather && !isLoading && (
          <div className="text-center py-16">
            <div className="bg-slate-800 rounded-full w-24 h-24 mx-auto mb-6 flex items-center justify-center border border-slate-700">
              <MapPin className="w-10 h-10 text-slate-500" />
            </div>
            <h2 className="text-2xl font-semibold text-white mb-2">
              Check Mandal Weather
            </h2>
            <p className="text-slate-400 max-w-md mx-auto mb-6">
              Enter a Mandal name to get accurate, real-time weather data for that specific area.
            </p>
            <div className="bg-slate-800 rounded-xl p-6 max-w-lg mx-auto border border-slate-700">
              <h3 className="text-white font-medium mb-3">Example Mandal Searches:</h3>
              <div className="space-y-2 text-left">
                <p className="text-emerald-400 text-sm">• Lakkireddipalle, Kadapa, Andhra Pradesh</p>
                <p className="text-emerald-400 text-sm">• Vempalle, Kadapa, Andhra Pradesh</p>
                <p className="text-emerald-400 text-sm">• Proddatur, Kadapa, Andhra Pradesh</p>
                <p className="text-emerald-400 text-sm">• Pulivendla, Kadapa, Andhra Pradesh</p>
                <p className="text-emerald-400 text-sm">• Rayachoti, Annamayya, Andhra Pradesh</p>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-slate-800 border-t border-slate-700 px-6 py-4 mt-auto">
        <div className="max-w-6xl mx-auto text-center text-slate-500 text-sm">
          Weather data provided by Open-Meteo API • Real-time weather conditions
        </div>
      </footer>
    </div>
  );
}

export default App;