import { WeatherData } from "../types/weather";
import { Droplets, Wind, Gauge, Cloud, Thermometer, MapPin } from "lucide-react";

interface WeatherDetailsProps {
  weather: WeatherData;
}

function DetailCard({ icon, label, value, sublabel }: { icon: React.ReactNode; label: string; value: string; sublabel?: string }) {
  return (
    <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 hover:border-emerald-600 transition-colors">
      <div className="flex items-start gap-4">
        <div className="bg-emerald-600/20 rounded-lg p-3 text-emerald-400">
          {icon}
        </div>
        <div>
          <p className="text-slate-400 text-sm mb-1">{label}</p>
          <p className="text-2xl font-semibold text-white">{value}</p>
          {sublabel && (
            <p className="text-slate-500 text-sm mt-1">{sublabel}</p>
          )}
        </div>
      </div>
    </div>
  );
}

export function WeatherDetails({ weather }: WeatherDetailsProps) {
  return (
    <>
      {/* Location Info Bar */}
      <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
        <div className="flex items-center gap-2 text-emerald-400 mb-2">
          <MapPin className="w-4 h-4" />
          <span className="font-medium">Location Details</span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-slate-500">Mandal:</span>
            <span className="text-white ml-2 font-medium">{weather.mandal || weather.region}</span>
          </div>
          {weather.district && (
            <div>
              <span className="text-slate-500">District:</span>
              <span className="text-white ml-2">{weather.district}</span>
            </div>
          )}
          {weather.state && (
            <div>
              <span className="text-slate-500">State:</span>
              <span className="text-white ml-2">{weather.state}</span>
            </div>
          )}
          <div>
            <span className="text-slate-500">Country:</span>
            <span className="text-white ml-2">{weather.country}</span>
          </div>
        </div>
      </div>

      {/* Weather Details Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <DetailCard
          icon={<Droplets className="w-5 h-5" />}
          label="Humidity"
          value={`${weather.humidity}%`}
          sublabel="Relative humidity"
        />
        <DetailCard
          icon={<Wind className="w-5 h-5" />}
          label="Wind Speed"
          value={`${weather.windSpeed} km/h`}
          sublabel={`Direction: ${weather.windDirection}`}
        />
        <DetailCard
          icon={<Gauge className="w-5 h-5" />}
          label="Pressure"
          value={`${weather.pressure} hPa`}
          sublabel="Mean sea level"
        />
        <DetailCard
          icon={<Cloud className="w-5 h-5" />}
          label="Cloud Cover"
          value={`${weather.cloudCover}%`}
          sublabel={weather.cloudCover > 70 ? "Mostly cloudy" : weather.cloudCover > 30 ? "Partly cloudy" : "Mostly clear"}
        />
        <DetailCard
          icon={<Thermometer className="w-5 h-5" />}
          label="Feels Like"
          value={`${weather.feelsLike}°C`}
          sublabel="Apparent temperature"
        />
        <DetailCard
          icon={<Clock className="w-5 h-5" />}
          label="Last Updated"
          value={weather.localTime}
          sublabel="Real-time data"
        />
      </div>
    </>
  );
}

function Clock({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}