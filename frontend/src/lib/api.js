import axios from "axios";
import { GAMES, SOURCES } from "../data/seed";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = BACKEND_URL ? `${BACKEND_URL}/api` : null;

const wrap = (data) => Promise.resolve({ data });
const allGames = [...GAMES];
const allSources = SOURCES;

const filterGames = (params) => {
  let games = [...allGames];
  const status = params.get("status");
  const genre = params.get("genre");
  const source = params.get("source");
  const search = params.get("search");
  const onlyCoop = params.get("only_coop") === "true";
  const onlyMulti = params.get("only_multi") === "true";

  if (status === "cracked") games = games.filter((g) => !g.is_coming_soon);
  if (status === "coming_soon") games = games.filter((g) => g.is_coming_soon);
  if (genre && genre.toLowerCase() !== "all") {
    games = games.filter((g) => g.genres?.some((x) => x.toLowerCase().includes(genre.toLowerCase())));
  }
  if (source) games = games.filter((g) => g.source === source);
  if (search) games = games.filter((g) => g.title.toLowerCase().includes(search.toLowerCase()));
  if (onlyCoop) games = games.filter((g) => g.is_coop);
  if (onlyMulti) games = games.filter((g) => g.is_multiplayer);

  games.sort((a, b) => {
    if (a.is_coming_soon !== b.is_coming_soon) return a.is_coming_soon ? 1 : -1;
    const scoreA = a.steam_score || 0;
    const scoreB = b.steam_score || 0;
    if (scoreA !== scoreB) return scoreB - scoreA;
    return a.title.localeCompare(b.title);
  });
  return games;
};

const localApi = {
  get: async (path) => {
    const [pathname, query = ""] = path.split("?");
    const params = new URLSearchParams(query);

    if (pathname === "/") return wrap({ name: "DrawCrack API", status: "ok" });
    if (pathname === "/games") return wrap(filterGames(params));
    if (pathname === "/games/stats") {
      const total = allGames.length;
      const cracked = allGames.filter((g) => !g.is_coming_soon).length;
      const comingSoon = allGames.filter((g) => g.is_coming_soon).length;
      const coop = allGames.filter((g) => g.is_coop).length;
      return wrap({ total, cracked, coming_soon: comingSoon, coop });
    }
    if (pathname === "/games/genres") {
      const counts = {};
      allGames.forEach((g) => {
        (g.genres || []).forEach((genre) => {
          counts[genre] = (counts[genre] || 0) + 1;
        });
      });
      const genres = Object.entries(counts)
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count);
      return wrap(genres);
    }
    if (pathname.startsWith("/games/")) {
      const id = pathname.replace("/games/", "");
      const game = allGames.find((g) => g.id === id);
      return wrap(game || null);
    }
    if (pathname === "/sources") return wrap(Object.values(allSources));
    if (pathname.startsWith("/sources/")) {
      const id = pathname.replace("/sources/", "");
      return wrap(allSources[id] || null);
    }
    return Promise.reject({ response: { data: { detail: "Not found" } } });
  },
  post: async (path) => {
    if (path.endsWith("/find-torrent")) {
      const id = path.replace("/games/", "").replace("/find-torrent", "").replace(/\/+$/, "");
      const game = allGames.find((g) => g.id === id);
      if (!game) {
        return Promise.reject({ response: { data: { detail: "Game not found" } } });
      }
      return Promise.reject({ response: { data: { detail: "البحث عن التورنت غير متوفر في النسخة الثابتة" } } });
    }
    return Promise.reject({ response: { data: { detail: "Action not supported offline" } } });
  },
};

const api = BACKEND_URL ? axios.create({ baseURL: API }) : localApi;
export default api;

export const SOURCE_STYLES = {
  "fitgirl":       { name: "FitGirl Repacks", color: "#ff4d96", bg: "rgba(255,77,150,0.12)", border: "rgba(255,77,150,0.4)" },
  "online-fix":    { name: "Online-Fix.me",   color: "#3b82f6", bg: "rgba(59,130,246,0.12)",  border: "rgba(59,130,246,0.4)" },
  "ankergames":    { name: "AnkerGames",       color: "#10b981", bg: "rgba(16,185,129,0.12)",  border: "rgba(16,185,129,0.4)" },
  "steamunlocked": { name: "SteamUnlocked",    color: "#06b6d4", bg: "rgba(6,182,212,0.12)",   border: "rgba(6,182,212,0.4)" },
};

export const ratingColor = (rating) => {
  if (!rating) return "rating-pos";
  if (typeof rating === "string") {
    const lo = rating.toLowerCase();
    if (lo.includes("overwhelmingly") || lo.includes("very positive")) return "rating-pos";
    if (lo.includes("mixed")) return "rating-mixed";
    if (lo.includes("negative")) return "rating-neg";
  }
  return "rating-pos";
};
