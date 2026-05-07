// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use tauri::Manager;

#[derive(Serialize, Deserialize, Debug)]
struct Build {
    build_id: String,
    status: String,
    current_phase: String,
    created_at: String,
    completed_at: Option<String>,
}

#[derive(Serialize, Deserialize, Debug)]
struct Gate {
    gate_id: String,
    status: String,
    passed_by: String,
    passed_at: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct SystemStats {
    total_builds: i64,
    completed_builds: i64,
    total_gates: i64,
    passed_gates: i64,
}

#[derive(Serialize, Deserialize, Debug)]
struct Agent {
    name: String,
}

#[tauri::command]
async fn fetch_builds() -> Result<Vec<Build>, String> {
    let client = reqwest::Client::new();
    let response = client
        .get("http://localhost:8081/api/builds")
        .send()
        .await
        .map_err(|e| format!("Failed to fetch builds: {}", e))?;
    
    let builds: Vec<Build> = response
        .json()
        .await
        .map_err(|e| format!("Failed to parse builds: {}", e))?;
    
    Ok(builds)
}

#[tauri::command]
async fn fetch_build_gates(build_id: String) -> Result<Vec<Gate>, String> {
    let client = reqwest::Client::new();
    let response = client
        .get(format!("http://localhost:8081/api/builds/{}/gates", build_id))
        .send()
        .await
        .map_err(|e| format!("Failed to fetch gates: {}", e))?;
    
    let gates: Vec<Gate> = response
        .json()
        .await
        .map_err(|e| format!("Failed to parse gates: {}", e))?;
    
    Ok(gates)
}

#[tauri::command]
async fn fetch_stats() -> Result<SystemStats, String> {
    let client = reqwest::Client::new();
    let response = client
        .get("http://localhost:8081/api/stats")
        .send()
        .await
        .map_err(|e| format!("Failed to fetch stats: {}", e))?;
    
    let stats: SystemStats = response
        .json()
        .await
        .map_err(|e| format!("Failed to parse stats: {}", e))?;
    
    Ok(stats)
}

#[tauri::command]
async fn fetch_agents() -> Result<Vec<Agent>, String> {
    let client = reqwest::Client::new();
    let response = client
        .get("http://localhost:8081/api/agents")
        .send()
        .await
        .map_err(|e| format!("Failed to fetch agents: {}", e))?;
    
    let agents: Vec<Agent> = response
        .json()
        .await
        .map_err(|e| format!("Failed to parse agents: {}", e))?;
    
    Ok(agents)
}

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            greet,
            fetch_builds,
            fetch_build_gates,
            fetch_stats,
            fetch_agents
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
