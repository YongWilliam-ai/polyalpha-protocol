export function DataCard({ label, value, unit, alert }) {
  return (
    <div className="bg-surface border border-gray-800 rounded-lg p-6 hover:border-gray-600 hover:bg-surface-hover transition-all duration-300 group">
      <div className="text-xs font-mono text-gray-500 uppercase tracking-wider mb-2">{label}</div>
      <div className={`text-2xl font-mono font-semibold group-hover:text-accent transition-colors ${
        alert ? "text-red-400" : "text-white"
      }`}>
        {value}
      </div>
      {unit && <div className="text-xs font-mono text-gray-600 mt-1">{unit}</div>}
    </div>
  );
}
