import { ForecastItem } from "../types/weather";

interface ForecastCardProps {
  forecast: ForecastItem;
}

export function ForecastCard({ forecast }: ForecastCardProps) {
  return (
    <div className="bg-slate-700 rounded-xl p-4 text-center hover:bg-slate-600 transition-colors border border-slate-600 hover:border-emerald-500">
      <p className="text-white font-medium mb-1">{forecast.day}</p>
      <p className="text-slate-500 text-xs mb-2">{forecast.date}</p>
      <div className="text-4xl mb-2">{forecast.conditionIcon}</div>
      <div className="flex justify-center items-baseline gap-2">
        <span className="text-white font-semibold text-lg">{forecast.high}°</span>
        <span className="text-slate-400 text-sm">/ {forecast.low}°</span>
      </div>
      <div className="mt-2 pt-2 border-t border-slate-600">
        <p className="text-xs text-slate-400">
          🌧️ {forecast.rainChance}% rain
        </p>
      </div>
    </div>
  );
}