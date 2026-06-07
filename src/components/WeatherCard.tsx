import { WeatherData } from "../types/weather";
import { MapPin, Clock, Thermometer, Coordinate } from "lucide-react";

interface WeatherCardProps {
  weather: WeatherData;
}

export function WeatherCard({ weather }: WeatherCardProps) {
  const getTemperatureColor = (temp: number): string => {
    if (temp <= 10) return "from-blue-600 to-cyan-700";
    if (temp <= 20) return "from-cyan-600 to-teal-700";
    if (temp <= 30) return "from-teal-600 to-emerald-700";
    if (temp <= 35) return "from-yellow-500 to-orange-600";
    return "from-orange-500 to-red-600";
  };

  return (
    <div className={`bg-gradient-to-br ${getTemperatureColor(weather.temperature)} rounded-2xl p-8 text-white shadow-xl`}>
      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
        {/* Left: Location & Temperature */}
        <div className="space-y-4">
          {/* Location Hierarchy - Mandal Level */}
          <div className="flex items-start gap-2 text-white/90">
            <MapPin className="w-5 h-5 mt-1 flex-shrink-0" />
            <div>
              <div className="text-2xl font-bold">{weather.mandal || weather.region}</div>
              <div className="text-white/80 text-sm mt-1">
                {weather.district && <span>District: {weather.district}</span>}
                {weather.state && <span> | State: {weather.state}</span>}
              </div>
              <div className="text-white/60 text-xs mt-1">
                {weather.country} • {weather.latitude.toFixed(4)}°N, {weather.longitude.toFixed(4)}°E
              </div>
            </div>
          </div>
          
          {/* Temperature */}
          <div className="flex items-baseline gap-2">
            <span className="text-7xl md:text-8xl font-bold tracking-tight">
              {weather.temperature}
            </span>
            <span className="text-3xl font-light">°C</span>
          </div>
          
          <div className="flex items-center gap-4 text-white/80">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              <span className="text-sm">Local time: {weather.localTime}</span>
            </div>
          </div>
        </div>

        {/* Right: Condition */}
        <div className="text-center lg:text-right bg-white/10 rounded-xl p-6 lg:min-w-[200px]">
          <div className="text-6xl mb-2">{weather.conditionIcon}</div>
          <div className="text-xl font-medium">{weather.condition}</div>
          <div className="flex items-center justify-center lg:justify-end gap-2 mt-3 text-white/80">
            <Thermometer className="w-4 h-4" />
            <span>Feels like {weather.feelsLike}°C</span>
          </div>
        </div>
      </div>
    </div>
  );
}