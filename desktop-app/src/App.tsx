import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";

interface Build {
  build_id: string;
  status: string;
  current_phase: string;
  created_at: string;
  completed_at?: string;
}

interface SystemStats {
  total_builds: number;
  completed_builds: number;
  total_gates: number;
  passed_gates: number;
}

function App() {
  const [builds, setBuilds] = useState<Build[]>([]);
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000);
    return () => clearInterval(interval);
  }, []);

  async function loadData() {
    try {
      setError(null);
      const [buildsData, statsData] = await Promise.all([
        invoke<Build[]>("fetch_builds"),
        invoke<SystemStats>("fetch_stats"),
      ]);
      setBuilds(buildsData);
      setStats(statsData);
      setLoading(false);
    } catch (err) {
      setError(`Error loading data: ${err}`);
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 to-purple-700 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-8 mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            19-Agent Build System Dashboard
          </h1>
          <p className="text-gray-600">Real-time build monitoring and status tracking</p>
        </div>

        {loading && <div className="text-white text-center">Loading...</div>}

        {error && (
          <div className="bg-red-500 text-white p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-gray-600 text-sm font-semibold uppercase mb-2">
                Total Builds
              </h3>
              <div className="text-4xl font-bold text-gray-800">{stats.total_builds}</div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-gray-600 text-sm font-semibold uppercase mb-2">
                Completed
              </h3>
              <div className="text-4xl font-bold text-gray-800">{stats.completed_builds}</div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-gray-600 text-sm font-semibold uppercase mb-2">
                Total Gates
              </h3>
              <div className="text-4xl font-bold text-gray-800">{stats.total_gates}</div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-gray-600 text-sm font-semibold uppercase mb-2">
                Gates Passed
              </h3>
              <div className="text-4xl font-bold text-gray-800">{stats.passed_gates}</div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Recent Builds</h2>
          {builds.length === 0 ? (
            <p className="text-gray-600">No builds found</p>
          ) : (
            <div className="space-y-4">
              {builds.map((build) => (
                <div
                  key={build.build_id}
                  className={`p-4 rounded-lg border-l-4 ${build.status === "COMPLETE"
                      ? "border-green-500 bg-green-50"
                      : "border-indigo-500 bg-gray-50"
                    }`}
                >
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-bold text-gray-800">{build.build_id}</span>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${build.status === "COMPLETE"
                          ? "bg-green-100 text-green-800"
                          : "bg-yellow-100 text-yellow-800"
                        }`}
                    >
                      {build.status}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600">
                    Phase: {build.current_phase} | Created:{" "}
                    {new Date(build.created_at).toLocaleString()}
                    {build.completed_at && (
                      <> | Completed: {new Date(build.completed_at).toLocaleString()}</>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
          <button
            onClick={loadData}
            className="mt-6 bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition"
          >
            Refresh
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
